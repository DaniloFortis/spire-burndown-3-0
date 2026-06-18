#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate 3.0.0 Bug Burndown Projection Dashboard

Creates an interactive 3-line projection chart:
- Ideal: What's required (zero by Code Freeze)
- Estimated: What's likely (historical rate)
- Actual: What's happening (daily reality)

Output: spire_3_0_projection_dashboard.html
"""

import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration
PROJECTIONS_FILE = "burndown_projections.json"
OUTPUT_HTML = "spire_3_0_projection_dashboard.html"


def load_projections():
    """Load projection data from JSON file."""
    print(f"📂 Loading projection data from {PROJECTIONS_FILE}...")
    with open(PROJECTIONS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Loaded projections generated on {data['generated_date']}")
    return data


def create_projection_chart(data):
    """
    Create 3-line projection chart with milestone markers.

    Args:
        data: Projection data dictionary

    Returns:
        plotly Figure
    """
    print("📊 Creating 3-line projection chart...")

    # Extract projection lines
    ideal = data['projections']['ideal']
    estimated = data['projections']['estimated']
    actual = data['projections']['actual']

    # Convert to separate lists for plotting
    ideal_dates = [datetime.strptime(p['date'], '%Y-%m-%d') for p in ideal]
    ideal_counts = [p['count'] for p in ideal]

    estimated_dates = [datetime.strptime(p['date'], '%Y-%m-%d') for p in estimated]
    estimated_counts = [p['count'] for p in estimated]

    actual_dates = [datetime.strptime(p['date'], '%Y-%m-%d') for p in actual]
    actual_counts = [p['count'] for p in actual]

    # Create figure
    fig = go.Figure()

    # Add Ideal line (solid black)
    fig.add_trace(go.Scatter(
        x=ideal_dates,
        y=ideal_counts,
        mode='lines',
        name='Ideal (Zero by Code Freeze)',
        line=dict(
            color='#000000',
            width=2
        ),
        hovertemplate='<b>Ideal</b><br>Date: %{x|%b %d}<br>Bugs: %{y:.0f}<extra></extra>'
    ))

    # Add Estimated line (light orange, dashed)
    fig.add_trace(go.Scatter(
        x=estimated_dates,
        y=estimated_counts,
        mode='lines',
        name='Estimated (Projection)',
        line=dict(
            color='#FFB366',
            width=3,
            dash='dash'
        ),
        hovertemplate='<b>Estimated</b><br>Date: %{x|%b %d}<br>Bugs: %{y:.0f}<extra></extra>'
    ))

    # Add Actual line (green, solid with markers)
    fig.add_trace(go.Scatter(
        x=actual_dates,
        y=actual_counts,
        mode='lines+markers',
        name='Actual (Daily Reality)',
        line=dict(
            color='#27AE60',
            width=4
        ),
        marker=dict(
            size=8,
            color='#27AE60',
            line=dict(
                color='white',
                width=2
            )
        ),
        hovertemplate='<b>Actual</b><br>Date: %{x|%b %d}<br>Bugs: %{y:.0f}<extra></extra>'
    ))

    # Add zero-date callouts for Ideal and Estimated lines
    # Ideal line zero date
    ideal = data['projections']['ideal']
    ideal_zero_point = next((p for p in ideal if p['count'] == 0), None)
    if ideal_zero_point:
        ideal_zero_date = datetime.strptime(ideal_zero_point['date'], '%Y-%m-%d')
        fig.add_annotation(
            x=ideal_zero_date,
            y=0,
            text=f"<b>Ideal hits zero</b><br>{ideal_zero_date.strftime('%b %d')}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor='#000000',
            ax=0,
            ay=-40,
            bgcolor='rgba(0, 0, 0, 0.8)',
            font=dict(size=10, color='white'),
            bordercolor='#000000',
            borderwidth=2,
            borderpad=4
        )

    # Estimated line zero date (calculate even if beyond projection window)
    estimated = data['projections']['estimated']
    estimated_zero_point = next((p for p in estimated if p['count'] == 0), None)

    if estimated_zero_point:
        # Zero point is within projection window
        estimated_zero_date = datetime.strptime(estimated_zero_point['date'], '%Y-%m-%d')
    else:
        # Calculate projected zero date beyond window
        last_estimated = estimated[-1]
        last_count = last_estimated['count']
        last_date = datetime.strptime(last_estimated['date'], '%Y-%m-%d')

        # Get the rate from projection data (negative = burning down)
        historical_rate = data.get('historical_daily_rate', -3.80)

        if historical_rate < 0:  # Negative rate means burning down
            days_to_zero = -last_count / historical_rate  # Both negative, result positive
            estimated_zero_date = last_date + timedelta(days=days_to_zero)
        else:
            estimated_zero_date = None  # Accumulating, won't reach zero

    if estimated_zero_date:
        # Position the callout at the end of chart if zero date is beyond go_live
        go_live_date = datetime.strptime(data['key_dates']['go_live'], '%Y-%m-%d')

        if estimated_zero_date <= go_live_date:
            # Zero date is within chart range
            callout_x = estimated_zero_date
            callout_y = 0
        else:
            # Zero date is beyond chart, position at end
            callout_x = go_live_date
            callout_y = estimated[-1]['count']

        fig.add_annotation(
            x=callout_x,
            y=callout_y,
            text=f"<b>Estimated hits zero</b><br>{estimated_zero_date.strftime('%b %d, %Y')}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor='#FFB366',
            ax=50,
            ay=-50,
            bgcolor='rgba(255, 179, 102, 0.9)',
            font=dict(size=10, color='white'),
            bordercolor='#FFB366',
            borderwidth=2,
            borderpad=4
        )

    # Add milestone markers
    milestones = data['key_dates']
    milestone_config = [
        {
            'key': 'code_freeze',
            'label': 'Code Freeze',
            'color': '#E74C3C',
            'position': 'top'
        },
        {
            'key': 'submit',
            'label': 'Submit',
            'color': '#E67E22',
            'position': 'top'
        },
        {
            'key': 'go_live',
            'label': 'Go Live',
            'color': '#27AE60',
            'position': 'top'
        }
    ]

    for milestone in milestone_config:
        date_str = milestones[milestone['key']]
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')

        # Add vertical line for milestone (original color with transparency, solid)
        # Convert hex color to rgba with transparency
        color_map = {
            '#E74C3C': 'rgba(231, 76, 60, 0.4)',   # Red with transparency
            '#E67E22': 'rgba(230, 126, 34, 0.4)',  # Orange with transparency
            '#27AE60': 'rgba(39, 174, 96, 0.4)'    # Green with transparency
        }

        fig.add_shape(
            type="line",
            x0=date_obj,
            x1=date_obj,
            y0=0,
            y1=0.95,  # Stop at 95% to leave room for text
            yref="paper",
            line=dict(
                color=color_map[milestone['color']],
                width=1.5
            )
        )

        # Add annotation - positioned at top of chart below legend
        fig.add_annotation(
            x=date_obj,
            y=1,
            yref="paper",
            text=f"<b>{milestone['label']}</b>",  # Bold text using HTML
            showarrow=False,
            yshift=-5,  # Small negative shift to position just below top
            font=dict(size=11, color=milestone['color'])
        )

    # Layout configuration
    fig.update_layout(
        title={
            'text': '🔥 Spire 3.0.0 Bug Burndown Projection',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 28, 'color': '#2C3E50'}
        },
        xaxis=dict(
            title='Date',
            gridcolor='#ECF0F1',
            showgrid=True,
            dtick=86400000,  # Show every day (milliseconds in a day)
            tickformat='%b %d',  # Format as "May 11"
            tickangle=-45  # Angle labels to fit better
        ),
        yaxis=dict(
            title='Active Bugs',
            gridcolor='#ECF0F1',
            showgrid=True,
            rangemode='tozero'
        ),
        hovermode='x unified',
        template='plotly_white',
        height=600,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(size=12)
        ),
        margin=dict(t=120, b=80, l=80, r=40)
    )

    return fig


def generate_summary_stats(data):
    """
    Generate HTML summary statistics box.

    Args:
        data: Projection data dictionary

    Returns:
        HTML string
    """
    print("📊 Generating summary statistics...")

    current_bugs = data['current_active_bugs']
    ideal_rate = data['ideal_rate_per_day']
    actual_2_0_rate = data.get('actual_2_0_rate', data['historical_daily_rate'])  # Use actual rate, fallback to historical
    estimated_line_rate = data.get('estimated_line_rate', data['historical_daily_rate'])  # Rate used for estimated line
    estimated_line_rate_source = data.get('estimated_line_rate_source', 'historical average')  # Source description
    business_days_to_freeze = data.get('business_days_to_code_freeze', data.get('days_to_code_freeze', 0))
    velocity_gap = data['metrics']['velocity_gap']

    # Calculate projected counts at key dates
    code_freeze_date = data['key_dates']['code_freeze']
    go_live_date = data['key_dates']['go_live']

    # Find estimated count at Code Freeze
    estimated_line = data['projections']['estimated']
    code_freeze_estimated = next(
        (p['count'] for p in estimated_line if p['date'] == code_freeze_date),
        None
    )

    html = f"""
    <div style="background: linear-gradient(135deg, #3B2A5C 0%, #2A1F42 100%); padding: 20px; border-radius: 10px; margin: 15px 0; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
            <div style="background-color: rgba(244, 197, 66, 0.15); padding: 15px; border-radius: 8px; text-align: center; border: 1px solid rgba(244, 197, 66, 0.3);">
                <h3 style="margin: 0; font-size: 11px; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px;">Active Bugs</h3>
                <p style="font-size: 32px; font-weight: bold; margin: 8px 0; color: #F4C542;">{current_bugs}</p>
                <p style="margin: 0; font-size: 10px; opacity: 0.7;">Excludes In QA · As of {data['generated_date']}</p>
            </div>
            <div style="background-color: rgba(244, 197, 66, 0.15); padding: 15px; border-radius: 8px; text-align: center; border: 1px solid rgba(244, 197, 66, 0.3);">
                <h3 style="margin: 0; font-size: 11px; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px;">Code Freeze</h3>
                <p style="font-size: 32px; font-weight: bold; margin: 8px 0; color: #F4C542;">{business_days_to_freeze}</p>
                <p style="margin: 0; font-size: 10px; opacity: 0.7;">business days remaining</p>
            </div>
            <div style="background-color: rgba(244, 197, 66, 0.15); padding: 15px; border-radius: 8px; text-align: center; border: 1px solid rgba(244, 197, 66, 0.3);">
                <h3 style="margin: 0; font-size: 11px; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px;">Required Bugs Fixed per Day</h3>
                <p style="font-size: 32px; font-weight: bold; margin: 8px 0; color: #F4C542;">{ideal_rate:.1f}</p>
                <p style="margin: 0; font-size: 10px; opacity: 0.7;">to hit zero by freeze</p>
            </div>
            <div style="background-color: rgba(244, 197, 66, 0.15); padding: 15px; border-radius: 8px; text-align: center; border: 1px solid rgba(244, 197, 66, 0.3);">
                <h3 style="margin: 0; font-size: 11px; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px;">{"Actual Fix/Find Delta" if estimated_line_rate_source == "last 10 business days" else "Estimated Fix/Find Delta"}</h3>
                <p style="font-size: 32px; font-weight: bold; margin: 8px 0; color: #F4C542;">{estimated_line_rate:+.2f}</p>
                <p style="margin: 0; font-size: 10px; opacity: 0.7;">{estimated_line_rate_source}</p>
            </div>
            <div style="background-color: rgba(244, 197, 66, 0.15); padding: 15px; border-radius: 8px; text-align: center; border: 1px solid rgba(244, 197, 66, 0.3);">
                <h3 style="margin: 0; font-size: 11px; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px;">Go Live</h3>
                <p style="font-size: 32px; font-weight: bold; margin: 8px 0; color: #F4C542;">{go_live_date}</p>
                <p style="margin: 0; font-size: 10px; opacity: 0.7;">Target date</p>
            </div>
        </div>
    </div>
    """

    return html


def generate_status_breakdown(data):
    """
    Generate HTML status breakdown cards (one per status with 1+ bugs).
    Includes In QA, excludes Closed and Won't Fix.

    Args:
        data: Projection data dictionary

    Returns:
        HTML string
    """
    print("🏷️  Generating status breakdown cards...")

    status_breakdown = data.get('status_breakdown', {})

    if not status_breakdown:
        return ""

    # Color palette for status badges - mapped to status semantics
    status_colors = {
        'to-do': '#7F8C8D',           # Gray - waiting to start
        'in progress': '#3498DB',     # Blue - actively being worked
        'in qa': '#9B59B6',           # Purple - in testing
        'qa review': '#9B59B6',       # Purple - QA workflow
        'code review': '#1ABC9C',     # Teal - code review
        'design review': '#16A085',   # Dark teal - design review
        'art review': '#E91E63',      # Pink - art review
        'build pending': '#F39C12',   # Orange - waiting for build
        'reopened': '#E74C3C',        # Red - regression
        'blocked': '#C0392B',         # Dark red - blocked
        'need more info': '#F1C40F',  # Yellow - awaiting info
    }

    # Build cards
    cards_html = ""
    for status, count in status_breakdown.items():
        status_lower = status.lower().strip()
        color = status_colors.get(status_lower, '#95A5A6')  # Default gray
        # Capitalize first letter of each word for display
        display_status = ' '.join(word.capitalize() for word in status.split())

        cards_html += f"""
            <div style="background-color: white; padding: 12px 16px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); border-left: 4px solid {color}; min-width: 130px; flex: 0 1 auto;">
                <div style="font-size: 10px; color: #7F8C8D; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-bottom: 4px;">{display_status}</div>
                <div style="font-size: 24px; font-weight: bold; color: {color}; line-height: 1;">{count}</div>
            </div>
        """

    html = f"""
    <div style="background-color: white; padding: 16px 20px; margin: 15px 0; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h3 style="margin: 0 0 12px 0; color: #2C3E50; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">📊 Bug Status Breakdown</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 10px;">
            {cards_html}
        </div>
    </div>
    """

    return html


def generate_dashboard(projections):
    """Generate complete HTML dashboard."""
    print("\n🚀 Generating dashboard HTML...")

    # Create chart
    fig = create_projection_chart(projections)

    # Generate summary stats
    summary_html = generate_summary_stats(projections)

    # Generate status breakdown cards
    status_breakdown_html = generate_status_breakdown(projections)

    # Combine into HTML
    print(f"\n💾 Saving dashboard to {OUTPUT_HTML}...")

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Spire 3.0.0 Bug Burndown Projection</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #F5F3F7;
        }}
        .header {{
            background: linear-gradient(135deg, #3B2A5C 0%, #2A1F42 100%);
            color: white;
            padding: 25px 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
        }}
        .header img {{
            height: 60px;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
            color: #F4C542;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        .header p {{
            margin: 5px 0 0 0;
            font-size: 14px;
            opacity: 0.8;
        }}
        .chart-container {{
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #7F8C8D;
            margin-top: 40px;
            font-size: 14px;
        }}
        .legend {{
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .legend h3 {{
            margin: 0 0 10px 0;
            color: #2C3E50;
            font-size: 16px;
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
            margin-bottom: 5px;
        }}
        .legend-line {{
            display: inline-block;
            width: 40px;
            height: 3px;
            vertical-align: middle;
            margin-right: 5px;
        }}
        .ideal-line {{ background-color: #000000; }}
        .estimated-line {{ background-color: #FFB366; border: 1px dashed #FFB366; height: 2px; }}
        .actual-line {{ background-color: #27AE60; }}
    </style>
</head>
<body>
    <div class="header">
        <img src="TwilightTowerslogo.png" alt="Twilight Towers Logo">
        <div>
            <h1>3.0.0 Bug Burndown Projection</h1>
        </div>
    </div>

    {summary_html}

    {status_breakdown_html}

    <div class="legend">
        <h3>📈 Understanding the Lines</h3>
        <div class="legend-item">
            <span class="legend-line ideal-line"></span>
            <strong style="color: #000000;">Ideal:</strong> Linear path to zero by Code Freeze (required rate: {projections['ideal_rate_per_day']:.1f} bugs/day)
        </div>
        <div class="legend-item">
            <span class="legend-line actual-line"></span>
            <strong style="color: #27AE60;">Actual:</strong> Real daily bug counts (transitions to Estimated)
        </div>
        <div class="legend-item">
            <span class="legend-line estimated-line"></span>
            <strong style="color: #FFB366;">Estimated:</strong> Future projection from last actual point
        </div>
    </div>

    <div class="chart-container">
        <div id="projection-chart"></div>
    </div>

    <div class="footer">
        <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        <p><strong>Data Source:</strong> ClickUp Spire 3.0.0 Bugs | Tracking Window: Jun 11 - Jul 6, 2026</p>
        <p style="margin-top: 10px; font-size: 12px; color: #95A5A6;">
            This projection uses historical find vs fix rates to estimate trajectory.
            The Actual line will update daily with real bug counts from ClickUp.
        </p>
    </div>

    <script>
        var plotlyData = {fig.to_json()};
        Plotly.newPlot('projection-chart', plotlyData.data, plotlyData.layout);
    </script>
</body>
</html>
""")

    print(f"✅ Dashboard saved successfully!")
    return OUTPUT_HTML


def main():
    """Main execution function."""
    print("🚀 Generating 3.0.0 Bug Burndown Projection Dashboard")
    print("="*60)

    # Load projection data
    projections = load_projections()

    # Generate dashboard
    dashboard_file = generate_dashboard(projections)

    # Print completion
    print("\n" + "="*60)
    print("✅ DASHBOARD GENERATION COMPLETE!")
    print("="*60)
    print(f"\n🎯 Open {dashboard_file} in your browser to view the projection chart")
    print("\nDashboard shows:")
    print("  • Ideal line (blue dashed) - Zero by Code Freeze")
    print("  • Estimated line (orange) - Historical rate projection")
    print("  • Actual line (green) - Real daily progress")
    print("  • Milestone markers for Code Freeze, Submit, Go Live")
    print("\n💡 The Actual line will be updated daily using update_actual_burndown.py")


if __name__ == "__main__":
    main()
