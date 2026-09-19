"""Conservative NVD CPE version applicability evaluator."""
from dataclasses import dataclass
import re
from typing import Optional

@dataclass(frozen=True)
class Applicability:
    status: str
    reason: str

def _tokens(v: str):
    v=(v or "").strip().lower()
    v=re.sub(r"^(rev[._ -]?|v(?=\d))","",v)
    if not v: return None
    parts=re.split(r"[._+\-]",v)
    out=[]
    for p in parts:
        if not p: continue
        m=re.fullmatch(r"(\d+)([a-z]+)?(\d*)",p)
        if not m: return None
        out.append((int(m.group(1)),m.group(2) or "",int(m.group(3)) if m.group(3) else -1))
    return tuple(out)

def compare_versions(a: str,b: str)->Optional[int]:
    ta,tb=_tokens(a),_tokens(b)
    if ta is None or tb is None: return None
    n=max(len(ta),len(tb)); zero=(0,"",-1)
    ta=ta+(zero,)*(n-len(ta)); tb=tb+(zero,)*(n-len(tb))
    return (ta>tb)-(ta<tb)

def evaluate_version(installed: str, match: dict)->Applicability:
    if not installed:
        return Applicability("not_assessable","installed version missing")
    criteria=[
        ("versionStartIncluding",lambda c:c>=0),
        ("versionStartExcluding",lambda c:c>0),
        ("versionEndIncluding",lambda c:c<=0),
        ("versionEndExcluding",lambda c:c<0),
    ]
    for key,pred in criteria:
        bound=match.get(key)
        if not bound: continue
        c=compare_versions(installed,bound)
        if c is None:
            return Applicability("potentially_affected",f"cannot safely compare {installed} with {key}={bound}")
        if not pred(c):
            return Applicability("not_affected",f"{installed} outside vulnerable range at {key}={bound}")
    # Exact CPE version, when criterion does not use wildcard/NA.
    crit=(match.get("criteria") or "")
    fields=crit.split(":")
    if len(fields)>=6 and fields[5] not in ("*","-",""):
        c=compare_versions(installed,fields[5])
        if c is None:
            return Applicability("potentially_affected","exact CPE version comparison ambiguous")
        return Applicability("confirmed_affected" if c==0 else "not_affected","exact CPE version criterion")
    if any(match.get(k) for k,_ in criteria):
        return Applicability("confirmed_affected","installed version satisfies vulnerable NVD range")
    return Applicability("potentially_affected","product criterion has no safely evaluable version boundary")
