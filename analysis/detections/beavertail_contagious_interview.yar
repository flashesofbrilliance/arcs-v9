rule DPRK_ContagiousInterview_BeaverTail_JS
{
    meta:
        author      = "Defensive CTI"
        description = "BeaverTail JS stealer / loader - Contagious Interview (G1052)"
        reference   = "MITRE S1246; ATT&CK G1052"
        tlp         = "CLEAR"

    strings:
        // hard indicators (this campaign)
        $ip     = "91.121.235.127"
        $port   = ":1224"
        $path   = "/api/checkStatus"
        $vercel = "vscode-check-mo4-ten.vercel.app"

        // behavioral (generalizes to variants)
        $b1 = "process.env"
        $b2 = /eval\s*\(\s*[a-zA-Z_$]/
        $b3 = ".vscode/tasks.json"
        $b4 = /axios|fetch|https?\.request/
        // MetaMask + common wallet extension IDs
        $w1 = "nkbihfbeogaeaoehlefnkodbefgpgknn"
        $w2 = "ejbalbakoplchlghecdalmeeeajnimhm"

    condition:
        // any pinned infra OR the stealer behavior cluster
        (1 of ($ip, $port, $path, $vercel))
        or ($b1 and $b2 and 1 of ($w1, $w2, $b4))
}
