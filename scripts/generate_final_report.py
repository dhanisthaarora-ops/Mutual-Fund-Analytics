"""
Generate the final Bluestock Mutual Fund Analytics PDF report.

The report uses the cleaned datasets, analytics outputs, and exported chart
images already present in the repository.
"""

from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHART_DIR = BASE_DIR / "reports" / "charts"
REPORT_PATH = BASE_DIR / "reports" / "Final_Report.pdf"


def load_data() -> dict[str, pd.DataFrame]:
    """Load datasets required for report metrics."""
    return {
        "fund_master": pd.read_csv(PROCESSED_DIR / "01_fund_master_clean.csv"),
        "nav": pd.read_csv(PROCESSED_DIR / "02_nav_history_clean.csv"),
        "aum": pd.read_csv(PROCESSED_DIR / "03_aum_by_fund_house_clean.csv"),
        "sip": pd.read_csv(PROCESSED_DIR / "04_monthly_sip_inflows_clean.csv"),
        "folio": pd.read_csv(PROCESSED_DIR / "06_industry_folio_count_clean.csv"),
        "performance": pd.read_csv(PROCESSED_DIR / "07_scheme_performance_clean.csv"),
        "transactions": pd.read_csv(PROCESSED_DIR / "08_investor_transactions_clean.csv"),
        "scorecard": pd.read_csv(PROCESSED_DIR / "fund_scorecard.csv"),
        "var": pd.read_csv(PROCESSED_DIR / "var_cvar_report.csv"),
    }


def metrics(data: dict[str, pd.DataFrame]) -> dict[str, object]:
    """Compute headline metrics used in the report."""
    aum = data["aum"].copy()
    sip = data["sip"].copy()
    folio = data["folio"].copy()
    scorecard = data["scorecard"].copy()
    var = data["var"].copy()

    aum["date"] = pd.to_datetime(aum["date"])
    sip["month"] = pd.to_datetime(sip["month"])
    folio["month"] = pd.to_datetime(folio["month"])

    latest_aum_date = aum["date"].max()
    latest_aum = aum.loc[aum["date"] == latest_aum_date, "aum_crore"].sum()
    latest_sip = sip.loc[sip["month"] == sip["month"].max(), "sip_inflow_crore"].sum()
    latest_folio = folio.loc[folio["month"] == folio["month"].max(), "total_folios_crore"].sum()
    total_schemes = int(aum.loc[aum["date"] == latest_aum_date, "num_schemes"].sum())
    top_fund = scorecard.sort_values("fund_score", ascending=False).iloc[0]
    worst_var = var.sort_values("var_95").iloc[0]

    return {
        "fund_count": len(data["fund_master"]),
        "nav_rows": len(data["nav"]),
        "transaction_rows": len(data["transactions"]),
        "latest_aum_lakh_cr": latest_aum / 100000,
        "latest_sip_cr": latest_sip,
        "latest_folio_cr": latest_folio,
        "total_schemes": total_schemes,
        "top_fund": top_fund,
        "worst_var": worst_var,
    }


def p(text: str, style: ParagraphStyle) -> Paragraph:
    """Create a paragraph."""
    return Paragraph(text, style)


def bullet_list(items: list[str], style: ParagraphStyle) -> list[Paragraph]:
    """Create bullet paragraphs."""
    return [Paragraph(f"- {item}", style) for item in items]


def image_if_exists(path: Path, width: float = 6.5 * inch) -> list[object]:
    """Return an image flowable if the file exists."""
    if not path.exists():
        return [Paragraph(f"Missing image: {path.name}", getSampleStyleSheet()["BodyText"])]
    img = Image(str(path))
    ratio = img.imageHeight / float(img.imageWidth)
    img.drawWidth = width
    img.drawHeight = width * ratio
    return [img]


def table_from_df(df: pd.DataFrame, columns: list[str], max_rows: int = 6) -> Table:
    """Create a styled ReportLab table from a DataFrame."""
    shown = df.loc[:, columns].head(max_rows).copy()
    for col in shown.select_dtypes(include="number").columns:
        shown[col] = shown[col].map(lambda value: f"{value:,.3f}")
    data = [columns] + shown.astype(str).values.tolist()
    tbl = Table(data, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B1F3A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D9E2EC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FA")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return tbl


def build_report() -> None:
    """Build the final PDF report."""
    data = load_data()
    m = metrics(data)

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontSize=26,
        leading=32,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0B1F3A"),
    )
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0B1F3A"),
        spaceAfter=12,
    )
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.5, leading=15, alignment=TA_LEFT)
    bullet = ParagraphStyle("Bullet", parent=body, leftIndent=14, firstLineIndent=-8, spaceAfter=5)

    story: list[object] = []
    story += [
        Spacer(1, 1.2 * inch),
        p("Bluestock Mutual Fund Analytics Capstone", title),
        Spacer(1, 0.25 * inch),
        p("Final Project Report", styles["Heading2"]),
        Spacer(1, 0.4 * inch),
        p("Prepared by: Dhanistha Arora", body),
        p("Tools: Python, pandas, SQLite, Power BI Service, Jupyter Notebook", body),
        p("Version: v1.0", body),
        PageBreak(),
    ]
    story += [
        p("1. Executive Summary", h1),
        p(
            "This project builds an end-to-end mutual fund analytics system for Bluestock. It transforms raw fund, NAV, SIP, AUM, investor transaction, benchmark, and portfolio holding data into cleaned datasets, a SQLite warehouse, analytical notebooks, risk metrics, recommender logic, and a four-page interactive dashboard.",
            body,
        ),
        Spacer(1, 0.15 * inch),
        table_from_df(
            pd.DataFrame(
                [
                    ["Funds covered", m["fund_count"]],
                    ["NAV records", f"{m['nav_rows']:,}"],
                    ["Investor transactions", f"{m['transaction_rows']:,}"],
                    ["Latest AUM", f"₹{m['latest_aum_lakh_cr']:.2f} lakh crore"],
                    ["Latest SIP inflow", f"₹{m['latest_sip_cr']:,.0f} crore"],
                    ["Latest folios", f"{m['latest_folio_cr']:.2f} crore"],
                    ["Schemes tracked", f"{m['total_schemes']:,}"],
                ],
                columns=["Metric", "Value"],
            ),
            ["Metric", "Value"],
            10,
        ),
        PageBreak(),
    ]
    story += [
        p("2. Data Sources", h1),
        *bullet_list(
            [
                "Fund master: AMFI code, fund house, scheme name, category, plan, risk grade, benchmark, and expense ratio.",
                "NAV history: daily NAV values used for returns, CAGR, VaR, CVaR, Sharpe, Sortino, drawdown, and benchmark comparison.",
                "AUM and SIP data: industry-level trend tables for AUM growth, SIP inflows, folios, and category flows.",
                "Investor transactions: investor-level transaction date, type, amount, state, city tier, age group, gender, and KYC status.",
                "Portfolio holdings and benchmarks: sector allocation, HHI concentration, Nifty 50 and Nifty 100 comparison series.",
            ],
            bullet,
        ),
        PageBreak(),
    ]
    story += [
        p("3. ETL Design", h1),
        p(
            "The ETL pipeline reads raw CSVs from data/raw, standardises dates and numeric values, removes duplicates, validates business rules, and writes cleaned outputs to data/processed. NAV history is sorted by AMFI code and date, invalid NAV values are removed, and missing calendar dates are forward-filled to handle weekends and holidays.",
            body,
        ),
        *bullet_list(
            [
                "NAV validation: date parsing, duplicate removal, NAV > 0 checks, and forward-fill after full date reindexing.",
                "Transaction validation: transaction type standardisation, amount > 0, KYC status checks, and date parsing.",
                "Performance validation: numeric return checks, expense ratio range checks, and anomaly flags.",
                "SQLite load: SQLAlchemy writes cleaned data to star-schema tables and verifies row counts.",
            ],
            bullet,
        ),
        PageBreak(),
    ]
    story += [
        p("4. SQLite Star Schema", h1),
        p(
            "The warehouse is designed around dimension and fact tables. dim_fund stores the fund master attributes and dim_date stores reusable calendar fields. Fact tables store NAV, transactions, performance, AUM, SIP inflow, category inflow, folio count, portfolio holdings, and benchmark values.",
            body,
        ),
        *bullet_list(
            [
                "Primary keys: dim_fund.amfi_code and dim_date.date.",
                "Main foreign keys: fact_nav.amfi_code, fact_transactions.amfi_code, fact_performance.amfi_code.",
                "SQL files: sql/schema.sql and sql/queries.sql document the database structure and analysis queries.",
            ],
            bullet,
        ),
        PageBreak(),
    ]
    story += [
        p("5. EDA Findings: Industry and SIP Trends", h1),
        p("EDA shows a strong upward trend in SIP participation and industry-level AUM. The dashboard highlights fund house dominance and month-level variation in category inflows.", body),
        *image_if_exists(CHART_DIR / "02_aum_growth_by_fund_house.png", 6.0 * inch),
        PageBreak(),
    ]
    story += [
        p("6. EDA Findings: Investor and Geography Patterns", h1),
        p("Investor analytics reveal meaningful differences across state, age group, city tier, and transaction type. SIP amount patterns vary by investor age group, while state-wise contribution is concentrated in major markets.", body),
        *image_if_exists(CHART_DIR / "08_sip_amount_by_state.png", 6.0 * inch),
        Spacer(1, 0.15 * inch),
        *image_if_exists(CHART_DIR / "06_sip_amount_by_age_group.png", 5.6 * inch),
        PageBreak(),
    ]
    story += [
        p("7. Performance Analysis", h1),
        p("Performance analytics cover CAGR, Sharpe ratio, Sortino ratio, Alpha, Beta, maximum drawdown, tracking error, and a composite scorecard.", body),
        table_from_df(
            data["scorecard"].sort_values("fund_score", ascending=False),
            ["scheme_name", "fund_house", "cagr_3yr", "sharpe_ratio", "alpha_annual", "fund_score"],
            6,
        ),
        Spacer(1, 0.2 * inch),
        *image_if_exists(CHART_DIR / "fund_scorecard_top10.png", 6.0 * inch),
        PageBreak(),
    ]
    story += [
        p("8. Advanced Risk Analytics", h1),
        p("The advanced analytics notebook computes Historical VaR and CVaR at 95%, rolling 90-day Sharpe, cohort behavior, SIP continuity risk, recommender outputs, and sector HHI concentration.", body),
        table_from_df(
            data["var"].sort_values("var_95"),
            ["scheme_name", "fund_house", "var_95", "cvar_95", "daily_volatility"],
            6,
        ),
        Spacer(1, 0.2 * inch),
        *image_if_exists(CHART_DIR / "rolling_sharpe_chart.png", 6.2 * inch),
        PageBreak(),
    ]
    story += [
        p("9. Dashboard Overview", h1),
        p("The dashboard was built in Power BI Service on Mac and contains four report pages: Industry Overview, Fund Performance, Investor Analytics, and SIP & Market Trends.", body),
        *bullet_list(
            [
                "Industry Overview: Total AUM, SIP inflow, folios, schemes, AUM trend, and AUM by AMC.",
                "Fund Performance: return-risk scatter, fund scorecard, NAV trend, and slicers.",
                "Investor Analytics: state-level transactions, transaction type split, age group SIP amount, and monthly volume.",
                "SIP & Market Trends: SIP inflow trend, Nifty 50 trend, and category inflow heatmap.",
            ],
            bullet,
        ),
        PageBreak(),
    ]
    for idx, (heading, filename) in enumerate(
        [
            ("10. Dashboard Screenshot: Industry Overview", "page1_industry_overview.png"),
            ("11. Dashboard Screenshot: Fund Performance", "page2_fund_performance.png"),
            ("12. Dashboard Screenshot: Investor Analytics", "page3_investor_analytics.png"),
            ("13. Dashboard Screenshot: SIP & Market Trends", "page4_sip_market_trends.png"),
        ]
    ):
        story += [p(heading, h1), *image_if_exists(CHART_DIR / filename, 6.7 * inch), PageBreak()]
    story += [
        p("14. Limitations", h1),
        *bullet_list(
            [
                "Power BI Desktop is not available natively on Mac, so the dashboard was built in Power BI Service.",
                "The browser workflow can export PDF and screenshots, but PBIX creation requires Windows Power BI Desktop.",
                "Some analysis outputs depend on the quality and completeness of the provided source datasets.",
                "SQLite database files are excluded from GitHub to keep the repository clean; schema.sql documents the database design.",
            ],
            bullet,
        ),
        PageBreak(),
    ]
    story += [
        p("15. Recommendations", h1),
        *bullet_list(
            [
                "Use scorecard ranking as a first-pass screening tool, then review fund mandate and portfolio concentration.",
                "Monitor SIP continuity flags to identify investors who may need engagement before drop-off.",
                "Use VaR and CVaR together because CVaR captures average losses during the worst return days.",
                "Track expense ratios alongside returns because low-cost funds with strong risk-adjusted returns improve long-term outcomes.",
                "Extend the project with scheduled NAV refresh, Streamlit dashboard, Monte Carlo simulation, and portfolio optimization.",
            ],
            bullet,
        ),
        PageBreak(),
    ]
    story += [
        p("16. Self-Review Checklist", h1),
        table_from_df(
            pd.DataFrame(
                [
                    ["ETL pipeline", "Complete"],
                    ["SQLite schema and SQL queries", "Complete"],
                    ["EDA notebook and charts", "Complete"],
                    ["Performance analytics and CSV outputs", "Complete"],
                    ["Power BI dashboard pages", "Complete in Power BI Service"],
                    ["Advanced analytics and recommender", "Complete"],
                    ["Final report and presentation", "Complete"],
                ],
                columns=["Objective", "Status"],
            ),
            ["Objective", "Status"],
            10,
        ),
        Spacer(1, 0.3 * inch),
        p("The project is ready for final GitHub submission with a v1.0 tag.", body),
    ]

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(REPORT_PATH),
        pagesize=A4,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )
    doc.build(story)
    print(f"Created {REPORT_PATH}")


if __name__ == "__main__":
    build_report()
