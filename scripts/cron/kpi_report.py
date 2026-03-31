#!/usr/bin/env python3
"""
KPI Report Script
Runs every Sunday at 7:00 PM to generate key performance indicator reports.
"""

import os
import sys
import logging
import datetime
from typing import Dict, List, Optional
import statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/kpi_report.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class KPIMetrics:
    """
    Class to handle KPI metrics collection and calculation
    """
    
    def __init__(self):
        self.metrics = {}
    
    def collect_productivity_metrics(self) -> Dict[str, any]:
        """
        Collect productivity-related KPIs
        """
        logger.info("Collecting productivity metrics...")
        
        # Placeholder for actual productivity data
        # In reality, this would integrate with:
        # - Time tracking systems
        # - Project management tools
        # - Code repository analytics
        # - Task completion systems
        
        productivity_kpis = {
            'hours_worked': 40.0,  # Placeholder
            'tasks_completed': 15,  # Placeholder
            'tasks_assigned': 18,   # Placeholder
            'completion_rate': 0.0,  # Will be calculated
            'project_velocity': 12.5,  # Placeholder
            'on_time_delivery_rate': 0.0,  # Will be calculated
            'focus_time_hours': 28.5,  # Placeholder
            'context_switches': 45,  # Placeholder
        }
        
        # Calculate derived metrics
        productivity_kpis['completion_rate'] = (
            productivity_kpis['tasks_completed'] / productivity_kpis['tasks_assigned'] * 100
            if productivity_kpis['tasks_assigned'] > 0 else 0
        )
        
        productivity_kpis['on_time_delivery_rate'] = 95.0  # Placeholder
        
        logger.info(f"Productivity metrics collected: {productivity_kpis}")
        return productivity_kpis
    
    def collect_quality_metrics(self) -> Dict[str, any]:
        """
        Collect quality-related KPIs
        """
        logger.info("Collecting quality metrics...")
        
        # Placeholder for actual quality data
        # In reality, this would integrate with:
        # - CI/CD pipeline metrics
        # - Code quality tools
        # - Testing frameworks
        # - Bug tracking systems
        
        quality_kpis = {
            'code_coverage': 85.5,  # Percentage
            'bugs_found_pre_release': 3,  # Placeholder
            'bugs_found_post_release': 1,  # Placeholder
            'security_vulnerabilities': 0,  # Placeholder
            'technical_debt_ratio': 12.3,  # Percentage
            'refactor_frequency': 5,  # Times per week
            'peer_review_coverage': 98.0,  # Percentage
            'build_success_rate': 96.7,  # Percentage
        }
        
        logger.info(f"Quality metrics collected: {quality_kpis}")
        return quality_kpis
    
    def collect_learning_metrics(self) -> Dict[str, any]:
        """
        Collect learning and development KPIs
        """
        logger.info("Collecting learning metrics...")
        
        # Placeholder for actual learning data
        # In reality, this would integrate with:
        # - Training platforms
        # - Certification systems
        # - Knowledge base contributions
        # - Mentoring activities
        
        learning_kpis = {
            'training_hours_completed': 8.0,  # Placeholder
            'courses_completed': 2,  # Placeholder
            'certifications_earned': 0,  # Placeholder
            'knowledge_articles_written': 3,  # Placeholder
            'mentoring_hours': 2.5,  # Placeholder
            'new_technologies_explored': 4,  # Placeholder
            'skills_assessed': 12,  # Placeholder
            'learning_goal_completion_rate': 75.0,  # Percentage
        }
        
        logger.info(f"Learning metrics collected: {learning_kpis}")
        return learning_kpis
    
    def collect_collaboration_metrics(self) -> Dict[str, any]:
        """
        Collect collaboration and communication KPIs
        """
        logger.info("Collecting collaboration metrics...")
        
        # Placeholder for actual collaboration data
        # In reality, this would integrate with:
        # - Communication platforms (Slack, Teams, etc.)
        # - Code review systems
        # - Meeting platforms
        # - Feedback systems
        
        collaboration_kpis = {
            'code_reviews_given': 12,  # Placeholder
            'code_reviews_received': 8,  # Placeholder
            'meetings_attended': 10,  # Placeholder
            'meetings_organized': 3,  # Placeholder
            'feedback_requests_sent': 5,  # Placeholder
            'feedback_requests_responded': 8,  # Placeholder
            'cross_team_collaborations': 4,  # Placeholder
            'communication_responsiveness': 4.2,  # Scale 1-5
        }
        
        logger.info(f"Collaboration metrics collected: {collaboration_kpis}")
        return collaboration_kpis


def calculate_kpi_trends(historical_data: List[Dict], current_kpis: Dict) -> Dict[str, any]:
    """
    Calculate trends based on historical KPI data
    """
    logger.info("Calculating KPI trends...")
    
    if not historical_data:
        # If no historical data, return neutral trends
        return {kpi: {'trend': 'neutral', 'change': 0.0, 'trend_strength': 0.0} 
                for kpi in current_kpis.keys()}
    
    trends = {}
    
    # For each KPI, compare with previous period
    for kpi_name, current_value in current_kpis.items():
        if isinstance(current_value, (int, float)):
            # Calculate average from historical data
            historical_values = [data.get(kpi_name, 0) for data in historical_data if kpi_name in data]
            
            if historical_values:
                avg_historical = statistics.mean(historical_values)
                
                # Calculate change
                change = current_value - avg_historical
                change_percentage = (change / avg_historical * 100) if avg_historical != 0 else 0
                
                # Determine trend direction
                if abs(change_percentage) < 5:  # Less than 5% change is neutral
                    trend = 'neutral'
                elif change_percentage > 0:
                    trend = 'positive'
                else:
                    trend = 'negative'
                
                trends[kpi_name] = {
                    'trend': trend,
                    'change': change,
                    'change_percentage': round(change_percentage, 2),
                    'trend_strength': min(abs(change_percentage) / 10, 1.0)  # Normalize to 0-1 scale
                }
            else:
                trends[kpi_name] = {'trend': 'neutral', 'change': 0.0, 'trend_strength': 0.0}
        else:
            # For non-numeric values, mark as neutral
            trends[kpi_name] = {'trend': 'neutral', 'change': 0.0, 'trend_strength': 0.0}
    
    logger.info(f"Trends calculated: {trends}")
    return trends


def generate_kpi_report(productivity: Dict, quality: Dict, learning: Dict, collaboration: Dict, trends: Dict) -> str:
    """
    Generate comprehensive KPI report
    """
    logger.info("Generating KPI report...")
    
    # Helper function to format trend indicators
    def get_trend_indicator(trend_info):
        if not trend_info:
            return "📊"
        trend = trend_info.get('trend', 'neutral')
        if trend == 'positive':
            return "📈"
        elif trend == 'negative':
            return "📉"
        else:
            return "📊"
    
    # Helper function to format value with trend
    def format_value_with_trend(value, kpi_name):
        trend_info = trends.get(kpi_name, {})
        indicator = get_trend_indicator(trend_info)
        change_pct = trend_info.get('change_percentage', 0)
        
        if change_pct != 0:
            return f"{value} {indicator} ({change_pct:+.1f}%)"
        else:
            return f"{value} {indicator}"
    
    report = f"""Weekly KPI Report
===============
Week of: {datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())}
Generated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Executive Summary:
------------------
This week's performance across key dimensions shows our progress toward organizational goals.
Each metric is tracked with trend analysis to identify improvement areas and successes.

Productivity Metrics:
--------------------
- Hours Worked: {format_value_with_trend(productivity['hours_worked'], 'hours_worked')}
- Tasks Completed: {format_value_with_trend(productivity['tasks_completed'], 'tasks_completed')}
- Tasks Assigned: {format_value_with_trend(productivity['tasks_assigned'], 'tasks_assigned')}
- Completion Rate: {format_value_with_trend(f"{productivity['completion_rate']:.1f}%", 'completion_rate')}
- Project Velocity: {format_value_with_trend(productivity['project_velocity'], 'project_velocity')}
- On-Time Delivery Rate: {format_value_with_trend(f"{productivity['on_time_delivery_rate']:.1f}%", 'on_time_delivery_rate')}
- Focus Time Hours: {format_value_with_trend(productivity['focus_time_hours'], 'focus_time_hours')}
- Context Switches: {format_value_with_trend(productivity['context_switches'], 'context_switches')}

Quality Metrics:
---------------
- Code Coverage: {format_value_with_trend(f"{quality['code_coverage']:.1f}%", 'code_coverage')}
- Bugs Found Pre-Release: {format_value_with_trend(quality['bugs_found_pre_release'], 'bugs_found_pre_release')}
- Bugs Found Post-Release: {format_value_with_trend(quality['bugs_found_post_release'], 'bugs_found_post_release')}
- Security Vulnerabilities: {format_value_with_trend(quality['security_vulnerabilities'], 'security_vulnerabilities')}
- Technical Debt Ratio: {format_value_with_trend(f"{quality['technical_debt_ratio']:.1f}%", 'technical_debt_ratio')}
- Refactor Frequency: {format_value_with_trend(quality['refactor_frequency'], 'refactor_frequency')}
- Peer Review Coverage: {format_value_with_trend(f"{quality['peer_review_coverage']:.1f}%", 'peer_review_coverage')}
- Build Success Rate: {format_value_with_trend(f"{quality['build_success_rate']:.1f}%", 'build_success_rate')}

Learning & Development:
----------------------
- Training Hours Completed: {format_value_with_trend(learning['training_hours_completed'], 'training_hours_completed')}
- Courses Completed: {format_value_with_trend(learning['courses_completed'], 'courses_completed')}
- Certifications Earned: {format_value_with_trend(learning['certifications_earned'], 'certifications_earned')}
- Knowledge Articles Written: {format_value_with_trend(learning['knowledge_articles_written'], 'knowledge_articles_written')}
- Mentoring Hours: {format_value_with_trend(learning['mentoring_hours'], 'mentoring_hours')}
- New Technologies Explored: {format_value_with_trend(learning['new_technologies_explored'], 'new_technologies_explored')}
- Skills Assessed: {format_value_with_trend(learning['skills_assessed'], 'skills_assessed')}
- Learning Goal Completion Rate: {format_value_with_trend(f"{learning['learning_goal_completion_rate']:.1f}%", 'learning_goal_completion_rate')}

Collaboration & Communication:
----------------------------
- Code Reviews Given: {format_value_with_trend(collaboration['code_reviews_given'], 'code_reviews_given')}
- Code Reviews Received: {format_value_with_trend(collaboration['code_reviews_received'], 'code_reviews_received')}
- Meetings Attended: {format_value_with_trend(collaboration['meetings_attended'], 'meetings_attended')}
- Meetings Organized: {format_value_with_trend(collaboration['meetings_organized'], 'meetings_organized')}
- Feedback Requests Sent: {format_value_with_trend(collaboration['feedback_requests_sent'], 'feedback_requests_sent')}
- Feedback Requests Responded: {format_value_with_trend(collaboration['feedback_requests_responded'], 'feedback_requests_responded')}
- Cross-Team Collaborations: {format_value_with_trend(collaboration['cross_team_collaborations'], 'cross_team_collaborations')}
- Communication Responsiveness: {format_value_with_trend(f"{collaboration['communication_responsiveness']:.1f}/5", 'communication_responsiveness')}

Top Performances:
----------------
"""
    
    # Identify top performing metrics
    all_metrics = {
        **productivity, **quality, **learning, **collaboration
    }
    
    # Find numeric metrics with positive trends
    top_performers = []
    for name, value in all_metrics.items():
        if isinstance(value, (int, float)) and name in trends:
            trend_info = trends[name]
            if trend_info['trend'] == 'positive':
                top_performers.append((name, value, trend_info['change_percentage']))
    
    # Sort by change percentage and take top 5
    top_performers.sort(key=lambda x: x[2], reverse=True)
    
    if top_performers:
        for i, (name, value, change) in enumerate(top_performers[:5]):
            report += f"- {name.replace('_', ' ').title()}: {value} (+{change:.1f}%)\n"
    else:
        report += "- No significantly improving metrics this week\n"
    
    report += f"""
Areas Needing Attention:
-----------------------
"""
    
    # Find metrics with negative trends or below threshold
    attention_areas = []
    for name, value in all_metrics.items():
        if isinstance(value, (int, float)) and name in trends:
            trend_info = trends[name]
            if trend_info['trend'] == 'negative':
                attention_areas.append((name, value, trend_info['change_percentage']))
    
    # Add metrics that might be below acceptable thresholds
    threshold_checks = [
        ('code_coverage', quality['code_coverage'], 80, 'low'),
        ('completion_rate', productivity['completion_rate'], 90, 'low'),
        ('on_time_delivery_rate', productivity['on_time_delivery_rate'], 95, 'low'),
        ('build_success_rate', quality['build_success_rate'], 95, 'low'),
        ('peer_review_coverage', quality['peer_review_coverage'], 90, 'low'),
    ]
    
    for name, value, threshold, condition in threshold_checks:
        if condition == 'low' and value < threshold:
            attention_areas.append((name, value, f"below threshold of {threshold}"))
    
    # Remove duplicates and sort
    attention_areas = list(set(attention_areas))
    attention_areas.sort(key=lambda x: x[2] if isinstance(x[2], (int, float)) else 0)
    
    if attention_areas:
        for i, (name, value, issue) in enumerate(attention_areas[:5]):
            if isinstance(issue, float):
                report += f"- {name.replace('_', ' ').title()}: {value} ({issue:+.1f}% change)\n"
            else:
                report += f"- {name.replace('_', ' ').title()}: {value} ({issue})\n"
    else:
        report += "- No critical areas requiring immediate attention\n"
    
    report += f"""
Recommendations:
---------------
Based on this week's KPIs, consider focusing on:
1. Maintain current momentum in top-performing areas
2. Address metrics requiring attention with targeted actions
3. Continue investing in learning and development
4. Monitor collaboration metrics for team effectiveness
5. Set specific goals for next week based on these insights

Next Week Goals:
---------------
- Set specific targets for improvement areas
- Continue strong performance in top areas
- Schedule review of attention areas with stakeholders
"""
    
    logger.info("KPI report generated")
    return report


def save_kpi_report(report: str) -> str:
    """
    Save the KPI report to a file
    """
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"reports/kpi_report_{timestamp}.md"
    
    # Ensure reports directory exists
    os.makedirs('reports', exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"KPI report saved to {filename}")
    return filename


def main():
    """
    Main execution function
    """
    logger.info("Starting KPI Report Process")
    
    try:
        # Initialize KPI metrics collector
        kpi_collector = KPIMetrics()
        
        # Collect all types of metrics
        productivity_metrics = kpi_collector.collect_productivity_metrics()
        quality_metrics = kpi_collector.collect_quality_metrics()
        learning_metrics = kpi_collector.collect_learning_metrics()
        collaboration_metrics = kpi_collector.collect_collaboration_metrics()
        
        # Calculate trends (using placeholder historical data)
        # In a real implementation, this would fetch from a database
        historical_data = []  # Would come from persistence layer
        current_kpis = {**productivity_metrics, **quality_metrics, 
                       **learning_metrics, **collaboration_metrics}
        trends = calculate_kpi_trends(historical_data, current_kpis)
        
        # Generate report
        report = generate_kpi_report(
            productivity_metrics, 
            quality_metrics, 
            learning_metrics, 
            collaboration_metrics,
            trends
        )
        
        # Save report
        report_file = save_kpi_report(report)
        
        logger.info(f"KPI Report completed successfully. Report: {report_file}")
        
        # Exit with success code
        return 0
        
    except Exception as e:
        logger.error(f"Error during KPI Report: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())