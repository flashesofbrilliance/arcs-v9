#!/usr/bin/env bash
# Example hook: gets one event as JSON on stdin. Prints a line for cast events only.
python3 -c 'import sys,json; e=json.load(sys.stdin); m=e.get("mergeMessageBody",{}).get("message",{}).get("data",{}); m.get("type")=="MESSAGE_TYPE_CAST_ADD" and print("HOOK cast fid",m["fid"])'
