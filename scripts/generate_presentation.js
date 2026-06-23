const pptxgen = require("/Users/dhanistha/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/pptxgenjs");
const path = require("path");

const baseDir = "/Users/dhanistha/mutual-fund-analytics";
const chartDir = path.join(baseDir, "reports", "charts");
const output = path.join(baseDir, "reports", "Bluestock_MF_Presentation.pptx");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Dhanistha Arora";
pptx.subject = "Bluestock Mutual Fund Analytics Capstone";
pptx.title = "Bluestock MF Presentation";
pptx.company = "Bluestock";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-US"
};

const COLORS = {
  navy: "0B1F3A",
  blue: "0078D4",
  green: "00A676",
  gray: "F5F7FA",
  text: "1F2933"
};

function title(slide, text) {
  slide.addText(text, {
    x: 0.45, y: 0.25, w: 12.2, h: 0.45,
    fontFace: "Aptos Display", fontSize: 24, bold: true,
    color: COLORS.navy, margin: 0
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 0.45, y: 0.82, w: 12.2, h: 0,
    line: { color: COLORS.blue, width: 1.3 }
  });
}

function bullets(slide, items, x, y, w, h, fontSize = 16) {
  slide.addText(items.map(t => ({ text: t, options: { bullet: { indent: 12 }, hanging: 4 } })), {
    x, y, w, h, fontSize, color: COLORS.text,
    fit: "shrink", valign: "top"
  });
}

function image(slide, file, x, y, w, h) {
  slide.addImage({ path: path.join(chartDir, file), x, y, w, h, sizingCrop: true });
}

function footer(slide, num) {
  slide.addText(`Bluestock MF Capstone | ${num}`, {
    x: 10.8, y: 7.05, w: 1.9, h: 0.2, fontSize: 8,
    color: "6B7280", align: "right", margin: 0
  });
}

let s;

s = pptx.addSlide();
s.background = { color: COLORS.gray };
s.addText("Bluestock Mutual Fund Analytics", {
  x: 0.7, y: 2.2, w: 11.8, h: 0.6, fontSize: 34,
  bold: true, color: COLORS.navy, align: "center", margin: 0
});
s.addText("Final Capstone Presentation", {
  x: 0.7, y: 2.95, w: 11.8, h: 0.35, fontSize: 20,
  color: COLORS.blue, align: "center", margin: 0
});
s.addText("Python | SQLite | Power BI | Advanced Analytics", {
  x: 0.7, y: 3.45, w: 11.8, h: 0.3, fontSize: 14,
  color: COLORS.text, align: "center", margin: 0
});
s.addText("Prepared by Dhanistha Arora", {
  x: 0.7, y: 4.15, w: 11.8, h: 0.3, fontSize: 14,
  color: COLORS.text, align: "center", margin: 0
});
footer(s, 1);

s = pptx.addSlide(); title(s, "Problem & Objective");
bullets(s, [
  "Build a complete mutual fund analytics system for Bluestock.",
  "Convert raw mutual fund data into cleaned, queryable, visual analytics outputs.",
  "Evaluate fund performance using CAGR, Sharpe, Sortino, Alpha, Beta, drawdown, VaR, and CVaR.",
  "Create an investor-friendly dashboard and final business recommendations."
], 0.8, 1.25, 11.6, 4.8);
footer(s, 2);

s = pptx.addSlide(); title(s, "Data Sources");
bullets(s, [
  "Fund master: AMFI code, fund house, category, plan, benchmark, risk grade.",
  "NAV history: daily NAV used for return and risk calculations.",
  "AUM, SIP inflow, category inflow, folio count, and benchmark datasets.",
  "Investor transactions: amount, state, city tier, age group, gender, payment mode, KYC.",
  "Portfolio holdings: sector exposure used for HHI concentration analysis."
], 0.8, 1.1, 11.8, 5.2);
footer(s, 3);

s = pptx.addSlide(); title(s, "Architecture");
bullets(s, [
  "Raw CSVs are stored in data/raw.",
  "Python ETL validates dates, numeric values, duplicates, NAV > 0, transaction amount > 0, and KYC values.",
  "Cleaned CSVs are written to data/processed.",
  "SQLite schema stores dim_fund, dim_date, fact_nav, fact_transactions, fact_performance, fact_aum, and supporting fact tables.",
  "Power BI Service consumes the cleaned Excel export for dashboarding."
], 0.8, 1.1, 11.8, 5.2);
footer(s, 4);

s = pptx.addSlide(); title(s, "EDA Highlights: Industry Growth");
image(s, "02_aum_growth_by_fund_house.png", 0.7, 1.1, 5.7, 4.7);
image(s, "04_category_inflow_heatmap.png", 6.7, 1.1, 5.7, 4.7);
bullets(s, [
  "AUM growth is concentrated among large AMCs.",
  "Category inflows vary materially by month and product category."
], 0.9, 6.0, 11.2, 0.8, 12);
footer(s, 5);

s = pptx.addSlide(); title(s, "EDA Highlights: Investors");
image(s, "08_sip_amount_by_state.png", 0.7, 1.05, 5.8, 4.6);
image(s, "06_sip_amount_by_age_group.png", 6.8, 1.05, 5.6, 4.6);
bullets(s, [
  "Top states contribute a large share of transaction value.",
  "SIP ticket size differs across age groups."
], 0.9, 5.95, 11.2, 0.8, 12);
footer(s, 6);

s = pptx.addSlide(); title(s, "Performance Metrics: Scorecard");
image(s, "fund_scorecard_top10.png", 0.8, 1.1, 6.0, 4.9);
bullets(s, [
  "Composite score combines 3-year return, Sharpe, Alpha, inverse expense ratio, and inverse maximum drawdown.",
  "The scorecard creates a simple rankable view for fund screening."
], 7.1, 1.35, 5.3, 3.4, 15);
footer(s, 7);

s = pptx.addSlide(); title(s, "Performance Metrics: Risk");
image(s, "daily_return_distribution.png", 0.75, 1.05, 5.7, 4.6);
image(s, "rolling_sharpe_chart.png", 6.75, 1.05, 5.8, 4.6);
bullets(s, [
  "Daily return distribution supports VaR and CVaR risk estimation.",
  "Rolling Sharpe reveals changing risk-adjusted performance over time."
], 0.9, 5.95, 11.2, 0.8, 12);
footer(s, 8);

s = pptx.addSlide(); title(s, "Dashboard Screenshots: Overview & Performance");
image(s, "page1_industry_overview.png", 0.7, 1.05, 5.8, 4.8);
image(s, "page2_fund_performance.png", 6.8, 1.05, 5.8, 4.8);
bullets(s, [
  "Industry Overview summarizes AUM, SIP inflows, folios, schemes, and AMC trends.",
  "Fund Performance compares returns, risk, scorecard ranks, and NAV movement."
], 0.9, 6.05, 11.2, 0.8, 12);
footer(s, 9);

s = pptx.addSlide(); title(s, "Dashboard Screenshots: Investors & Market Trends");
image(s, "page3_investor_analytics.png", 0.7, 1.05, 5.8, 4.8);
image(s, "page4_sip_market_trends.png", 6.8, 1.05, 5.8, 4.8);
bullets(s, [
  "Investor Analytics explores state, transaction type, age group, and transaction volume.",
  "SIP & Market Trends compares SIP inflow, Nifty 50, and category inflows."
], 0.9, 6.05, 11.2, 0.8, 12);
footer(s, 10);

s = pptx.addSlide(); title(s, "Key Findings");
bullets(s, [
  "Large AMCs dominate industry AUM, with SBI among the strongest visible players.",
  "SIP inflows and folios show rising investor participation over the project period.",
  "Risk-adjusted performance differs meaningfully across funds even when returns look similar.",
  "VaR and CVaR identify funds with larger downside tail risk.",
  "Investor cohort and SIP continuity analysis can support targeted retention actions."
], 0.9, 1.2, 11.4, 5.4, 16);
footer(s, 11);

s = pptx.addSlide();
s.background = { color: COLORS.navy };
s.addText("Thank You", {
  x: 0.7, y: 2.5, w: 11.8, h: 0.7, fontSize: 40,
  bold: true, color: "FFFFFF", align: "center", margin: 0
});
s.addText("Bluestock Mutual Fund Analytics Capstone", {
  x: 0.7, y: 3.35, w: 11.8, h: 0.35, fontSize: 18,
  color: "D9E2EC", align: "center", margin: 0
});
s.addText("GitHub repository includes ETL, SQLite schema, notebooks, dashboard exports, report, and presentation.", {
  x: 1.5, y: 4.05, w: 10.3, h: 0.5, fontSize: 13,
  color: "FFFFFF", align: "center", margin: 0
});
footer(s, 12);

pptx.writeFile({ fileName: output });
