// floorlight: a menu-bar traffic light for how long you have held the floor on a call.
// v0: loudness-based voice detection on two channels, no LLM, no network, nothing saved.
// Same rule as floorlight.py: your turn runs until the other side speaks for
// RESET_SECS without a real pause (about 4 words); backchannels do not end it.
//
// Build:  swiftc -O floorlight.swift -o floorlight        (Xcode Command Line Tools)
// Run:    ./floorlight [--yellow 40] [--red 60] [--mic-db -42] [--sys-db -50] [--meter]
// macOS 13+. First run asks for Microphone and Screen & System Audio Recording
// for your terminal app. Stdout gets one "turn Ns" line per finished turn.

import AppKit
import AVFoundation
import CoreMedia
import ScreenCaptureKit

setvbuf(stdout, nil, _IOLBF, 0)
let argv = CommandLine.arguments
func arg(_ name: String, _ def: Double) -> Double {
    guard let i = argv.firstIndex(of: name), i + 1 < argv.count,
          let v = Double(argv[i + 1]) else { return def }
    return v
}
let YELLOW = arg("--yellow", 40), RED = arg("--red", 60)
let MIC_DB = arg("--mic-db", -42), SYS_DB = arg("--sys-db", -50)
let METER = argv.contains("--meter")
let RESET_SECS = 1.2   // them, unbroken: a real reply, not "mm-hmm"
let ME_SECS = 0.3      // you, unbroken: ignore coughs and clicks
let HANGOVER = 0.35    // a gap this short is still the same stretch of speech

func now() -> Double { ProcessInfo.processInfo.systemUptime }

func rmsDB(_ p: UnsafePointer<Float>, _ n: Int) -> Double {
    guard n > 0 else { return -120 }
    var s: Float = 0
    for i in 0..<n { s += p[i] * p[i] }
    return 10 * log10(Double(s / Float(n)) + 1e-12)
}

/// One channel: is it speaking, and for how long without a real pause.
final class Voice {
    let threshold: Double
    var runStart = 0.0, lastLoud = -1e9, level = -120.0
    init(_ threshold: Double) { self.threshold = threshold }
    func feed(_ db: Double, at t: Double) {
        level = db
        guard db > threshold else { return }
        if t - lastLoud > HANGOVER { runStart = t }
        lastLoud = t
    }
    func active(_ t: Double) -> Bool { t - lastLoud <= HANGOVER }
    func run(_ t: Double) -> Double { active(t) ? t - runStart : 0 }
}

let mic = Voice(MIC_DB), sys = Voice(SYS_DB)
var mineSince: Double? = nil   // when you took the floor; nil = not yours
var presenting = false
var turns: [Double] = []

// --- menu bar ---
let app = NSApplication.shared
app.setActivationPolicy(.accessory)
let item = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)

func show(_ symbol: String, _ color: NSColor) {
    item.button?.attributedTitle = NSAttributedString(string: symbol, attributes: [
        .foregroundColor: color, .font: NSFont.systemFont(ofSize: 15)])
}

func summary() {
    let s = turns.sorted()
    guard !s.isEmpty else { print("no turns"); return }
    func p(_ q: Double) -> Int { Int(s[Int((q * Double(s.count - 1)).rounded())]) }
    print("turns n=\(s.count) median \(p(0.5))s p75 \(p(0.75))s p90 \(p(0.9))s max \(p(1))s")
}

final class Menu: NSObject {
    @objc func togglePresenting(_ sender: NSMenuItem) {
        presenting.toggle()
        sender.state = presenting ? .on : .off
        mineSince = nil
    }
    @objc func quit(_ sender: Any?) { summary(); app.terminate(nil) }
}
let menuTarget = Menu()
let menu = NSMenu()
let pres = NSMenuItem(title: "Presenting (pause light)",
                      action: #selector(Menu.togglePresenting(_:)), keyEquivalent: "p")
let quitItem = NSMenuItem(title: "Quit", action: #selector(Menu.quit(_:)), keyEquivalent: "q")
pres.target = menuTarget
quitItem.target = menuTarget
menu.addItem(pres)
menu.addItem(quitItem)
item.menu = menu
show("○", .secondaryLabelColor)

// --- the clock, 10 times a second ---
var lastMeter = 0.0
Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { _ in
    let t = now()
    if METER && t - lastMeter >= 1 {
        lastMeter = t
        print(String(format: "meter mic %.0f dB  sys %.0f dB", mic.level, sys.level))
    }
    if presenting { show("◐", .secondaryLabelColor); return }
    if sys.run(t) >= RESET_SECS, let since = mineSince {
        let held = t - sys.run(t) - since   // your turn ended when they started
        turns.append(held)
        print(String(format: "turn %.0fs", held))
        mineSince = nil
    } else if mineSince == nil, mic.run(t) >= ME_SECS, !sys.active(t) {
        mineSince = t - mic.run(t)          // echo guard: only while they are quiet
    }
    guard let since = mineSince else { show("○", .secondaryLabelColor); return }
    let held = t - since
    show("●", held < YELLOW ? .systemGreen : held < RED ? .systemYellow : .systemRed)
}

// --- your mic ---
let engine = AVAudioEngine()
AVCaptureDevice.requestAccess(for: .audio) { ok in
    guard ok else { print("microphone permission denied"); return }
    DispatchQueue.main.async {
        let input = engine.inputNode
        input.installTap(onBus: 0, bufferSize: 1024,
                         format: input.outputFormat(forBus: 0)) { buf, _ in
            guard let ch = buf.floatChannelData else { return }
            let db = rmsDB(ch[0], Int(buf.frameLength)), t = now()
            DispatchQueue.main.async { mic.feed(db, at: t) }
        }
        do { try engine.start() } catch { print("mic failed: \(error)") }
    }
}

// --- the call's audio (everything the Mac plays) ---
final class SystemAudio: NSObject, SCStreamOutput, SCStreamDelegate {
    var stream: SCStream?
    func start() async throws {
        let content = try await SCShareableContent.excludingDesktopWindows(
            false, onScreenWindowsOnly: true)
        guard let display = content.displays.first else { return }
        let cfg = SCStreamConfiguration()
        cfg.capturesAudio = true
        cfg.excludesCurrentProcessAudio = true
        cfg.channelCount = 1
        cfg.width = 2; cfg.height = 2                         // video is unused
        cfg.minimumFrameInterval = CMTime(value: 1, timescale: 1)
        let s = SCStream(filter: SCContentFilter(display: display, excludingWindows: []),
                         configuration: cfg, delegate: self)
        try s.addStreamOutput(self, type: .audio,
                              sampleHandlerQueue: DispatchQueue(label: "sys-audio"))
        try await s.startCapture()
        stream = s
    }
    func stream(_ stream: SCStream, didOutputSampleBuffer sb: CMSampleBuffer,
                of type: SCStreamOutputType) {
        guard type == .audio else { return }
        let t = now()
        try? sb.withAudioBufferList { abl, _ in
            guard let b = abl.first, let d = b.mData else { return }
            let n = Int(b.mDataByteSize) / MemoryLayout<Float>.size
            let db = rmsDB(d.assumingMemoryBound(to: Float.self), n)
            DispatchQueue.main.async { sys.feed(db, at: t) }
        }
    }
    func stream(_ stream: SCStream, didStopWithError error: Error) {
        print("system audio stopped: \(error.localizedDescription)")
    }
}
let systemAudio = SystemAudio()
Task {
    do { try await systemAudio.start() } catch {
        print("system audio failed (grant Screen & System Audio Recording): \(error)")
    }
}

print("floorlight running: yellow \(Int(YELLOW))s, red \(Int(RED))s. Quit from the menu bar.")
app.run()
