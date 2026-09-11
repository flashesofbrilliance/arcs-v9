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

        // behavioral (hunt-grade, not alert-grade)
        $b1 = "process.env"
        $b2 = /eval\s*\(\s*[a-zA-Z_$]/
        // MetaMask + common wallet extension IDs
        $w1 = "nkbihfbeogaeaoehlefnkodbefgpgknn"
        $w2 = "ejbalbakoplchlghecdalmeeeajnimhm"

    condition:
        // pinned infra alerts; the behavioral branch is hunt-only,
        // wallet ID is load-bearing to keep process.env+eval from
        // false-positing on ordinary Node tooling
        (1 of ($ip, $port, $path, $vercel))
        or ($b1 and $b2 and 1 of ($w1, $w2))
}
