#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate interactive burndown dashboard for Spire 3.0.0 release.

Creates an HTML dashboard with:
- Burndown chart showing cumulative open bugs
- Daily bugs opened vs closed
- Milestone distribution
- Key 3.0.0 dates overlaid
"""

import json
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration
BURNDOWN_DATA_FILE = "burndown_data.json"
OUTPUT_HTML = "spire_3_0_burndown_dashboard.html"


def load_burndown_data():
    """Load burndown data from JSON file."""
    print(f"📂 Loading burndown data from {BURNDOWN_DATA_FILE}...")
    with open(BURNDOWN_DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Loaded data for {data['total_bugs_in_window']} bugs")
    return data


def create_burndown_chart(data):
    """
    Create burndown chart showing cumulative open bugs over time.

    Args:
        data: Burndown data dictionary

    Returns:
        plotly Figure
    """
    # Extract cumulative data
    cumulative = data['cumulative_open_bugs']
    dates = sorted(cumulative.keys())
    counts = [cumulative[d] for d in dates]

    # Convert dates to datetime for plotting
    date_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates]

    # Create figure
    fig = go.Figure()

    # Add cumulative open bugs line
    fig.add_trace(go.Scatter(
        x=date_objs,
        y=counts,
        mode='lines',
        name='Open Bugs',
        line=dict(color='#E74C3C', width=3),
        fill='tozeroy',
        fillcolor='rgba(231, 76, 60, 0.1)'
    ))

    # Add milestone markers
    milestones = data['key_milestone_dates']
    milestone_colors = {
        '3.0.0_bug_fixing_only': '#F39C12',
        '3.0.0_code_freeze': '#E67E22',
        '3.0.0_submit': '#9B59B6',
        '3.0.0_go_live': '#27AE60'
    }
    milestone_names = {
        '3.0.0_bug_fixing_only': 'Bug Fixing Only',
        '3.0.0_code_freeze': 'Code Freeze',
        '3.0.0_submit': 'Submit',
        '3.0.0_go_live': 'Go Live'
    }

    for key, date_str in milestones.items():
        date_obj = datetime.fromisoformat(date_str)
        # Only show if in date range
        if date_objs[0] <= date_obj <= date_objs[-1]:
            # Find the bug count at this date
            closest_date = min(dates, key=lambda d: abs(datetime.strptime(d, '%Y-%m-%d') - date_obj))
            bug_count = cumulative[closest_date]

            fig.add_vline(
                x=date_obj,
                line_dash="dash",
                line_color=milestone_colors.get(key, '#95A5A6'),
                line_width=2,
                annotation_text=milestone_names.get(key, key),
                annotation_position="top"
            )

    # Layout
    fig.update_layout(
        title={
            'text': '🔥 Spire 3.0.0 Bug Burndown Chart',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24}
        },
        xaxis_title='Date',
        yaxis_title='Open Bugs',
        hovermode='x unified',
        template='plotly_white',
        height=600
    )

    return fig


def create_daily_activity_chart(data):
    """
    Create chart showing daily bugs opened vs closed.

    Args:
        data: Burndown data dictionary

    Returns:
        plotly Figure
    """
    # Get all dates from both opened and closed
    opened_dates = set(data['bugs_opened_by_date'].keys())
    closed_dates = set(data['bugs_closed_by_date'].keys())
    all_dates = sorted(opened_dates | closed_dates)

    # Convert to datetime and get counts
    date_objs = [datetime.strptime(d, '%Y-%m-%d') for d in all_dates]
    opened_counts = [data['bugs_opened_by_date'].get(d, 0) for d in all_dates]
    closed_counts = [data['bugs_closed_by_date'].get(d, 0) for d in all_dates]

    # Create figure
    fig = go.Figure()

    # Add opened bugs
    fig.add_trace(go.Bar(
        x=date_objs,
        y=opened_counts,
        name='Bugs Opened',
        marker_color='#E74C3C',
        opacity=0.7
    ))

    # Add closed bugs (negative for visual effect)
    fig.add_trace(go.Bar(
        x=date_objs,
        y=[-c for c in closed_counts],
        name='Bugs Closed',
        marker_color='#27AE60',
        opacity=0.7
    ))

    # Layout
    fig.update_layout(
        title={
            'text': '📊 Daily Bug Activity (Opened vs Closed)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Date',
        yaxis_title='Bug Count',
        hovermode='x unified',
        template='plotly_white',
        barmode='relative',
        height=500
    )

    return fig


def create_milestone_distribution_chart(data):
    """
    Create pie chart showing bug distribution by milestone.

    Args:
        data: Burndown data dictionary

    Returns:
        plotly Figure
    """
    # Get top 10 milestones
    milestone_counts = data['milestone_counts']
    sorted_milestones = sorted(milestone_counts.items(), key=lambda x: x[1], reverse=True)
    top_10 = sorted_milestones[:10]

    # Separate labels and values
    labels = [m[0] for m in top_10]
    values = [m[1] for m in top_10]

    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        marker=dict(
            colors=['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6',
                    '#1ABC9C', '#E67E22', '#34495E', '#16A085', '#D35400']
        )
    )])

    fig.update_layout(
        title={
            'text': '🎯 Top 10 Milestones by Bug Count',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        template='plotly_white',
        height=500
    )

    return fig


def create_status_distribution_chart(data):
    """
    Create bar chart showing bug distribution by status.

    Args:
        data: Burndown data dictionary

    Returns:
        plotly Figure
    """
    # Get status counts
    status_counts = data['status_counts']
    sorted_statuses = sorted(status_counts.items(), key=lambda x: x[1], reverse=True)

    labels = [s[0] for s in sorted_statuses]
    values = [s[1] for s in sorted_statuses]

    # Create bar chart
    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        marker_color='#3498DB',
        text=values,
        textposition='auto',
    )])

    fig.update_layout(
        title={
            'text': '📈 Bug Status Distribution',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Status',
        yaxis_title='Count',
        template='plotly_white',
        height=500
    )

    return fig


def generate_summary_stats(data):
    """
    Generate HTML summary statistics.

    Args:
        data: Burndown data dictionary

    Returns:
        HTML string
    """
    total = data['total_bugs_in_window']
    closed = data['status_counts'].get('Closed', 0)
    open_bugs = total - closed
    close_rate = (closed / total * 100) if total > 0 else 0

    # Get 3.0.0 specific bugs
    bugs_3_0_0 = data['milestone_counts'].get('3.0.0', 0)

    # Get critical dates
    milestones = data['key_milestone_dates']
    code_freeze = datetime.fromisoformat(milestones['3.0.0_code_freeze']).strftime('%B %d, %Y')
    go_live = datetime.fromisoformat(milestones['3.0.0_go_live']).strftime('%B %d, %Y')

    html = f"""
    <div style="background-color: #ECF0F1; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h2 style="text-align: center; color: #2C3E50;">📊 Summary Statistics</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px;">
            <div style="background-color: white; padding: 20px; border-radius: 8px; text-align: center;">
                <h3 style="color: #3498DB; margin: 0;">Total Bugs</h3>
                <p style="font-size: 36px; font-weight: bold; margin: 10px 0; color: #2C3E50;">{total}</p>
                <p style="color: #7F8C8D; margin: 0;">In 6-month window</p>
            </div>
            <div style="background-color: white; padding: 20px; border-radius: 8px; text-align: center;">
                <h3 style="color: #27AE60; margin: 0;">Closed</h3>
                <p style="font-size: 36px; font-weight: bold; margin: 10px 0; color: #27AE60;">{closed}</p>
                <p style="color: #7F8C8D; margin: 0;">{close_rate:.1f}% closure rate</p>
            </div>
            <div style="background-color: white; padding: 20px; border-radius: 8px; text-align: center;">
                <h3 style="color: #E74C3C; margin: 0;">Open</h3>
                <p style="font-size: 36px; font-weight: bold; margin: 10px 0; color: #E74C3C;">{open_bugs}</p>
                <p style="color: #7F8C8D; margin: 0;">Still in progress</p>
            </div>
            <div style="background-color: white; padding: 20px; border-radius: 8px; text-align: center;">
                <h3 style="color: #9B59B6; margin: 0;">3.0.0</h3>
                <p style="font-size: 36px; font-weight: bold; margin: 10px 0; color: #9B59B6;">{bugs_3_0_0}</p>
                <p style="color: #7F8C8D; margin: 0;">Tagged bugs</p>
            </div>
        </div>
        <div style="background-color: white; padding: 20px; border-radius: 8px; margin-top: 20px;">
            <h3 style="color: #2C3E50; margin-top: 0;">🎯 Key 3.0.0 Milestone Dates</h3>
            <ul style="list-style: none; padding: 0;">
                <li style="padding: 8px 0; border-bottom: 1px solid #ECF0F1;">
                    <strong style="color: #F39C12;">Bug Fixing Only:</strong>
                    <span style="color: #7F8C8D;">{datetime.fromisoformat(milestones['3.0.0_bug_fixing_only']).strftime('%B %d, %Y')}</span>
                </li>
                <li style="padding: 8px 0; border-bottom: 1px solid #ECF0F1;">
                    <strong style="color: #E67E22;">Code Freeze:</strong>
                    <span style="color: #7F8C8D;">{code_freeze}</span>
                </li>
                <li style="padding: 8px 0; border-bottom: 1px solid #ECF0F1;">
                    <strong style="color: #9B59B6;">Submit:</strong>
                    <span style="color: #7F8C8D;">{datetime.fromisoformat(milestones['3.0.0_submit']).strftime('%B %d, %Y')}</span>
                </li>
                <li style="padding: 8px 0;">
                    <strong style="color: #27AE60;">Go Live:</strong>
                    <span style="color: #7F8C8D;">{go_live}</span>
                </li>
            </ul>
        </div>
    </div>
    """

    return html


def generate_dashboard():
    """Generate complete interactive dashboard."""
    print("\n🚀 Generating Spire 3.0.0 Burndown Dashboard...\n")

    # Load data
    data = load_burndown_data()

    # Generate charts
    print("📊 Creating burndown chart...")
    burndown_fig = create_burndown_chart(data)

    print("📊 Creating daily activity chart...")
    daily_fig = create_daily_activity_chart(data)

    print("📊 Creating milestone distribution chart...")
    milestone_fig = create_milestone_distribution_chart(data)

    print("📊 Creating status distribution chart...")
    status_fig = create_status_distribution_chart(data)

    print("📊 Generating summary statistics...")
    summary_html = generate_summary_stats(data)

    # Combine into single HTML
    print(f"\n💾 Saving dashboard to {OUTPUT_HTML}...")

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Spire 3.0.0 Bug Burndown Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #F8F9FA;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 42px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 18px;
            opacity: 0.9;
        }}
        .chart-container {{
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #7F8C8D;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔥 Spire 3.0.0 Bug Burndown Dashboard</h1>
        <p>Analysis Period: November 21, 2025 - May 21, 2026 (6 months)</p>
    </div>

    {summary_html}

    <div class="chart-container">
        <div id="burndown-chart"></div>
    </div>

    <div class="chart-container">
        <div id="daily-activity-chart"></div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div class="chart-container">
            <div id="milestone-chart"></div>
        </div>
        <div class="chart-container">
            <div id="status-chart"></div>
        </div>
    </div>

    <div class="footer">
        <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        <p>Data Source: ClickUp Spire Bugs | Analysis by Claude Code</p>
    </div>

    <script>
        {burndown_fig.to_html(include_plotlyjs=False, div_id='burndown-chart')}
        {daily_fig.to_html(include_plotlyjs=False, div_id='daily-activity-chart')}
        {milestone_fig.to_html(include_plotlyjs=False, div_id='milestone-chart')}
        {status_fig.to_html(include_plotlyjs=False, div_id='status-chart')}
    </script>
</body>
</html>
""")

    print(f"✅ Dashboard saved successfully!")
    print(f"\n🎯 Open {OUTPUT_HTML} in your browser to view the dashboard")
    print("\n" + "="*60)
    print("✅ DASHBOARD GENERATION COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    generate_dashboard()
