from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


def pct(v): return "n/a" if v is None else f"{v:+.1%}"
def num(v): return "n/a" if v is None else f"{v:,.0f}"
def money(v): return "n/a" if v is None else f"${v:,.0f}"


def report_to_html(markdown: str) -> str:
    def inline(text: str) -> str:
        value = html.escape(text)
        value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
        value = re.sub(r"`(.+?)`", r"<code>\1</code>", value)
        return value
    parts, in_list = [], False
    for line in markdown.splitlines():
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            if in_list: parts.append("</ul>"); in_list = False
            parts.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("- "):
            if not in_list: parts.append("<ul>"); in_list = True
            parts.append(f"<li>{inline(line[2:])}</li>")
        elif line:
            if in_list: parts.append("</ul>"); in_list = False
            parts.append(f"<p>{inline(line)}</p>")
    if in_list: parts.append("</ul>")
    return "".join(parts)


def svg_grouped_bars(rows, categories, series, value_key, title, percent=False):
    width, height, pad = 760, 320, 55
    values = [r[value_key] for r in rows if r.get(value_key) is not None]
    vmax = max(values) * 1.15 if values else 1
    group_w = (width - 2*pad) / max(len(categories), 1)
    bar_w = min(44, group_w / (len(series)+1))
    colors = ["#236887", "#E8782F", "#2E7D4A", "#8B5FBF"]
    marks=[]
    for i,cat in enumerate(categories):
        subset=[r for r in rows if r.get("category")==cat]
        for j,s in enumerate(series):
            rec=next((r for r in subset if r.get("series")==s),None)
            if not rec: continue
            value=rec[value_key]; bh=(value/vmax)*(height-2*pad); x=pad+i*group_w+(j+0.5)*bar_w; y=height-pad-bh
            label=f"{value:.1%}" if percent else f"{value:,.0f}"
            marks.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w-4:.1f}" height="{bh:.1f}" rx="3" fill="{colors[j%len(colors)]}"/><text x="{x+bar_w/2-2:.1f}" y="{max(y-6,14):.1f}" text-anchor="middle" class="value">{label}</text>')
        marks.append(f'<text x="{pad+(i+.5)*group_w:.1f}" y="{height-20}" text-anchor="middle" class="axis">{html.escape(str(cat))}</text>')
    legend=''.join(f'<span><i style="background:{colors[i%len(colors)]}"></i>{html.escape(s)}</span>' for i,s in enumerate(series))
    return f'<section class="panel"><h2>{html.escape(title)}</h2><div class="legend">{legend}</div><svg viewBox="0 0 {width} {height}" role="img"><line x1="{pad}" y1="{height-pad}" x2="{width-pad}" y2="{height-pad}" class="grid"/>{"".join(marks)}</svg></section>'


def build_report(data):
    monthly=data["monthly"]; first,last=monthly[0],monthly[-1]; mom=data.get("latest_mom",{})
    trial_growth=last["trials"]/first["trials"]-1; sub_growth=last["subscriptions"]/first["subscriptions"]-1
    lines=[f'# {data["project"]["title"]}', '', '## Executive summary', '',
           f'Growth is positive, but acquisition volume is growing faster than subscriptions. From {first["month"]} to {last["month"]}, trials increased {trial_growth:.1%} while subscriptions increased {sub_growth:.1%}.',
           f'In the latest month, average daily trials changed {pct(mom.get("avg_daily_trials"))}, average daily subscriptions {pct(mom.get("avg_daily_subscriptions"))}, and average DAU {pct(mom.get("avg_dau"))}.', '',
           '## KPI scorecard', '',
           f'- Average daily trials: {num(last["avg_daily_trials"])} ({pct(mom.get("avg_daily_trials"))} vs prior month)',
           f'- Average daily subscriptions: {num(last["avg_daily_subscriptions"])} ({pct(mom.get("avg_daily_subscriptions"))} vs prior month)',
           f'- Average DAU: {num(last["avg_dau"])} ({pct(mom.get("avg_dau"))} vs prior month)',
           f'- Trial conversion: {last["trial_conversion"]:.1%}', f'- Feature adoption rate: {last["feature_adoption_rate"]:.1%}', '',
           '## Growth trajectory', '',
           f'Trial conversion moved from {first["trial_conversion"]:.1%} to {last["trial_conversion"]:.1%}. Feature adoption remained at {first["feature_adoption_rate"]:.1%}–{last["feature_adoption_rate"]:.1%}, and sessions per active user moved from {first["sessions_per_active"]:.2f} to {last["sessions_per_active"]:.2f}.', '',
           '## Detailed insights', '']
    latest_month=last["month"]; segments=[r for r in data["paid_segment"] if r["month"]==latest_month]
    if segments:
        best=min(segments,key=lambda r:r["cost_per_subscription"] if r["cost_per_subscription"] is not None else float('inf'))
        lines += [f'1. **Paid efficiency differs materially by segment.** {best["segment"]} has the lowest latest cost per subscription at {money(best["cost_per_subscription"])}.',
                  '2. **Conversion quality should be monitored alongside volume.** Trial growth that outpaces subscription growth lowers funnel efficiency.',
                  '3. **Stable engagement is a guardrail.** Feature adoption and sessions per active user indicate whether growth is diluting product depth.', '']
    lines += ['## Executive takeaways and decisions', '',
              '- Protect paid investment where subscription efficiency is stable.',
              '- Use controlled tests or caps where spend grows faster than subscriptions.',
              '- Diagnose targeting, trial quality, onboarding, pricing, and conversion before broadly increasing budget.',
              '- Treat cost per subscription as acquisition efficiency, not ROI.', '',
              '## Data validation', '', f'Validation status: **{data["validation_summary"]["status"]}**.', '']
    for issue in data["validation_summary"].get("issues",[]): lines.append(f'- {issue["dataset"]}: {issue["issue"]} Treatment: {issue["treatment"]}')
    lines += ['', '## Definitions and limitations', '']
    for k,v in data.get("definitions",{}).items(): lines.append(f'- **{k.replace("_"," ").title()}:** {v}')
    lines += ['', 'Revenue, margin, retention, cancellations, and lifetime value are required for ROI, payback, or profitability conclusions. Without them, assess trajectory and relative acquisition efficiency only.', '', '## Sources', '']
    for role,profile in data["validation_summary"]["datasets"].items(): lines.append(f'- {role}: `{profile["path"]}` ({str(profile["first_date"])[:10]} to {str(profile["last_date"])[:10]})')
    return '\n'.join(lines)


def build_html(data, report):
    last=data["monthly"][-1]; mom=data.get("latest_mom",{})
    cards=[("Average daily trials",num(last["avg_daily_trials"]),pct(mom.get("avg_daily_trials"))), ("Average daily subscriptions",num(last["avg_daily_subscriptions"]),pct(mom.get("avg_daily_subscriptions"))), ("Daily active users",num(last["avg_dau"]),pct(mom.get("avg_dau"))), ("Paid spend",money(last["spend"]),pct(mom.get("spend")))]
    card_html=''.join(f'<article class="card"><span>{html.escape(a)}</span><strong>{b}</strong><em>{c} vs prior month</em></article>' for a,b,c in cards)
    first=data["monthly"][0]
    growth=[]
    for r in data["monthly"]:
        for label,key in [("Trials","avg_daily_trials"),("Subscriptions","avg_daily_subscriptions"),("DAU","avg_dau")]: growth.append({"category":r["month"],"series":label,"value":r[key]/first[key]*100})
    seg=[]
    for r in data["paid_segment"]:
        if r["month"] in data["months"][-2:]: seg.append({"category":r["segment"],"series":r["month"],"value":r["cost_per_subscription"]})
    conv=[{"category":r["channel"],"series":"Conversion","value":r["conversion_rate"]} for r in data["channel_conversion_latest"]]
    charts=svg_grouped_bars(growth,data["months"],["Trials","Subscriptions","DAU"],"value","Growth trajectory index (first month = 100)")+svg_grouped_bars(seg,sorted({r["category"] for r in seg}),data["months"][-2:],"value","Paid cost per subscription by segment")+svg_grouped_bars(conv,[r["category"] for r in conv],["Conversion"],"value","Latest trial-to-subscription conversion",True)
    rows=''.join(f'<tr><td>{html.escape(r["segment"])}</td><td>{money(r["spend"])}</td><td>{num(r["subscriptions"])}</td><td>{money(r["cost_per_subscription"])}</td></tr>' for r in data["paid_segment"] if r["month"]==data["months"][-1])
    report_html=report_to_html(report)
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(data['project']['title'])}</title><style>
    :root{{--navy:#17324d;--blue:#236887;--ink:#1f2933;--muted:#62717d;--line:#d9e2e8;--bg:#f5f7f9}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,sans-serif}}header{{background:var(--navy);color:white;padding:30px max(24px,calc((100% - 1240px)/2))}}header h1{{margin:0;font-size:30px}}main{{max-width:1240px;margin:auto;padding:24px}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}}.card,.panel,.report{{background:white;border:1px solid var(--line);border-radius:12px;padding:18px}}.card span,.card em{{display:block;color:var(--muted)}}.card strong{{display:block;font-size:28px;color:var(--navy);margin:10px 0}}.card em{{font-style:normal;font-weight:650}}.charts{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px}}.panel:nth-child(3){{grid-column:1/-1}}h2{{color:var(--navy)}}svg{{width:100%;height:auto}}.axis,.value{{font-size:11px;fill:var(--muted)}}.value{{font-weight:650;fill:var(--ink)}}.grid{{stroke:var(--line)}}.legend{{display:flex;gap:16px;flex-wrap:wrap}}.legend i{{display:inline-block;width:10px;height:10px;margin-right:5px;border-radius:2px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;border-bottom:1px solid var(--line);text-align:left}}.report{{margin-top:16px}}.report li{{margin:6px 0}}@media(max-width:800px){{.cards,.charts{{grid-template-columns:1fr}}.panel:nth-child(3){{grid-column:auto}}}}
    </style></head><body><header><h1>{html.escape(data['project']['title'])}</h1><div>{html.escape(data['project']['audience'])} · {html.escape(data['months'][0])} to {html.escape(data['months'][-1])}</div></header><main><section class="cards">{card_html}</section><section class="charts">{charts}</section><section class="panel"><h2>Latest paid efficiency</h2><table><thead><tr><th>Segment</th><th>Spend</th><th>Subscriptions</th><th>Cost / subscription</th></tr></thead><tbody>{rows}</tbody></table></section><article class="report">{report_html}</article></main></body></html>'''


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--analysis",default="outputs/analysis_results.json"); parser.add_argument("--report",default="outputs/executive_report.md"); parser.add_argument("--dashboard",default="outputs/executive_dashboard.html"); args=parser.parse_args()
    data=json.loads(Path(args.analysis).read_text()); report=build_report(data); Path(args.report).write_text(report); Path(args.dashboard).write_text(build_html(data,report)); print(f"Report -> {args.report}\nDashboard -> {args.dashboard}")


if __name__=="__main__": main()
