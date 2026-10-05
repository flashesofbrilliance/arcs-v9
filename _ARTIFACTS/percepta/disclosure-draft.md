# Draft disclosure note (not sent) — routed through Talor

**To:** Talor Steinberg (ask him to relay to the right person at Percepta)
**Subject:** Something unrelated to the role, worth flagging to Percepta

---

Hi Talor,

Separate from everything else, I noticed something while going through the coding challenge
at challenge.percepta.ai that I think is worth passing along to someone at Percepta, not
related to my candidacy either way.

Running `cd /` in the challenge's virtual terminal moves out of the intended sandbox and
appears to reach the host filesystem, rather than staying contained to the challenge
environment. From there I could see what look like sibling session directories for other
candidates (named like player_xxxxx), alongside the one for my own session. I tried entering
a couple of them out of curiosity and got permission denied, so the underlying access control
seems to be doing its job even though the `cd` boundary itself is looser than I'd expect. I
didn't push further than that.

I'm not sure if this is a known or intentional part of the challenge or an actual boundary
issue worth fixing, so I wanted to flag it either way rather than guess. Could you pass it
along to whoever handles that, or point me to someone directly?

Thanks,
Zach
