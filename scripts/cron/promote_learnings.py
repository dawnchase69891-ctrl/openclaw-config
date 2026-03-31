#!/usr/bin/env python3
"""
Promote Learnings Script
Runs every Sunday at 8:00 PM to promote and share learned insights.
"""

import os
import sys
import logging
import datetime
from typing import Dict, List, Optional
import json
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/promote_learnings.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class LearningPromoter:
    """
    Class to handle identification and promotion of valuable learnings
    """
    
    def __init__(self):
        self.learning_sources = [
            'memory/',  # Daily memory files
            'notes/',   # Notes directory
            'reports/', # Generated reports
            'docs/'     # Documentation
        ]
    
    def discover_valuable_learnings(self) -> List[Dict[str, any]]:
        """
        Discover valuable learnings from various sources
        """
        logger.info("Discovering valuable learnings...")
        
        learnings = []
        
        # Look for recent learnings in memory files
        memory_dir = 'memory/'
        if os.path.exists(memory_dir):
            for filename in os.listdir(memory_dir):
                if filename.endswith('.md') and 'learned' in filename.lower():
                    filepath = os.path.join(memory_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Extract learning patterns
                        learning_blocks = self._extract_learning_blocks(content)
                        for block in learning_blocks:
                            learnings.append({
                                'source': filepath,
                                'type': 'discovered_learning',
                                'title': block.get('title', 'Untitled Learning'),
                                'content': block.get('content', ''),
                                'timestamp': block.get('timestamp', ''),
                                'tags': block.get('tags', []),
                                'importance': self._calculate_importance(block.get('content', ''))
                            })
        
        # Look for insights in reports
        reports_dir = 'reports/'
        if os.path.exists(reports_dir):
            for filename in os.listdir(reports_dir):
                if filename.startswith('learning_summary') or filename.startswith('kpi_report'):
                    filepath = os.path.join(reports_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Extract key insights
                        insights = self._extract_insights(content)
                        for insight in insights:
                            learnings.append({
                                'source': filepath,
                                'type': 'report_insight',
                                'title': insight.get('title', 'Key Insight'),
                                'content': insight.get('content', ''),
                                'timestamp': datetime.datetime.now().isoformat(),
                                'tags': ['insight', 'report'],
                                'importance': self._calculate_importance(insight.get('content', ''))
                            })
        
        # Filter for high-value learnings
        valuable_learnings = [l for l in learnings if l['importance'] >= 7]
        
        logger.info(f"Discovered {len(valuable_learnings)} valuable learnings")
        return valuable_learnings
    
    def _extract_learning_blocks(self, content: str) -> List[Dict[str, any]]:
        """
        Extract learning blocks from content
        """
        blocks = []
        
        # Pattern to match learning entries
        learning_pattern = r'##\s*(.*?)[\n\r]+(.*?)(?=\n##|\Z)'
        matches = re.findall(learning_pattern, content, re.DOTALL)
        
        for title, content_block in matches:
            # Extract tags if present
            tag_pattern = r'#(\w+)'
            tags = re.findall(tag_pattern, content_block)
            
            blocks.append({
                'title': title.strip(),
                'content': content_block.strip(),
                'timestamp': datetime.datetime.now().isoformat(),
                'tags': list(set(tags))
            })
        
        return blocks
    
    def _extract_insights(self, content: str) -> List[Dict[str, any]]:
        """
        Extract insights from report content
        """
        insights = []
        
        # Look for common insight sections
        insight_sections = [
            'Key Insights:',
            'Learning Outcomes:',
            'Areas for Improvement:',
            'Recommendations:',
            'Strengths Identified:'
        ]
        
        for section in insight_sections:
            pattern = rf'{re.escape(section)}\s*\n((?:- .*\n?)*)'
            matches = re.findall(pattern, content)
            
            for match in matches:
                items = re.findall(r'- (.*)', match)
                for item in items:
                    insights.append({
                        'title': section.replace(':', '').strip(),
                        'content': item.strip(),
                        'timestamp': datetime.datetime.now().isoformat()
                    })
        
        return insights
    
    def _calculate_importance(self, content: str) -> int:
        """
        Calculate importance score for a learning (scale 1-10)
        """
        score = 5  # Base score
        
        # Increase score for actionable content
        actionable_keywords = ['implement', 'apply', 'use', 'try', 'adopt', 'introduce']
        for keyword in actionable_keywords:
            if keyword in content.lower():
                score += 1
        
        # Increase score for specific metrics or data
        if re.search(r'\d+(?:\.\d+)?%', content):  # Percentages
            score += 1
        if re.search(r'\$\d+', content):  # Dollar amounts
            score += 1
        if re.search(r'\d+\s*(?:hour|day|week|month)', content):  # Time references
            score += 1
        
        # Increase score for technical depth
        technical_keywords = ['algorithm', 'architecture', 'framework', 'protocol', 'optimization', 'performance']
        for keyword in technical_keywords:
            if keyword in content.lower():
                score += 1
        
        # Cap at 10
        return min(score, 10)
    
    def prioritize_learnings(self, learnings: List[Dict]) -> List[Dict]:
        """
        Prioritize learnings based on importance and relevance
        """
        logger.info("Prioritizing learnings...")
        
        # Sort by importance score (descending), then by length of content (descending)
        prioritized = sorted(learnings, key=lambda x: (-x['importance'], -len(x['content'])))
        
        logger.info(f"Prioritized {len(prioritized)} learnings")
        return prioritized
    
    def format_for_promotion(self, learning: Dict) -> Dict[str, any]:
        """
        Format learning for promotion across channels
        """
        logger.info(f"Formatting learning for promotion: {learning.get('title', 'Unknown')}")
        
        # Create different formats for different channels
        formatted = {
            'title': learning['title'],
            'summary': self._create_summary(learning['content']),
            'full_content': learning['content'],
            'tags': learning['tags'],
            'importance': learning['importance'],
            'source': learning['source'],
            'timestamp': learning['timestamp'],
            'channels': {
                'blog': self._format_for_blog(learning),
                'social': self._format_for_social(learning),
                'internal': self._format_for_internal(learning),
                'documentation': self._format_for_documentation(learning)
            }
        }
        
        return formatted
    
    def _create_summary(self, content: str) -> str:
        """
        Create a summary of the learning content
        """
        # Take first 200 characters or first paragraph, whichever is shorter
        paragraphs = content.split('\n\n')
        first_para = paragraphs[0] if paragraphs else content
        
        if len(first_para) <= 200:
            return first_para
        else:
            return first_para[:197] + '...'
    
    def _format_for_blog(self, learning: Dict) -> str:
        """
        Format learning for blog post
        """
        blog_format = f"""# {learning['title']}

## Introduction
{self._create_summary(learning['content'])}

## Details
{learning['content']}

## Key Takeaways
- Actionable insight 1
- Actionable insight 2
- Actionable insight 3

## Conclusion
Applying these learnings can help improve our processes and outcomes.

*Originally discovered on: {learning['timestamp']}*
"""
        return blog_format
    
    def _format_for_social(self, learning: Dict) -> str:
        """
        Format learning for social media (concise)
        """
        # Limit to 280 characters for Twitter-like platforms
        content = f"💡 {learning['title']}: {self._create_summary(learning['content'])}"
        if len(content) > 280:
            content = content[:277] + '...'
        
        return content
    
    def _format_for_internal(self, learning: Dict) -> str:
        """
        Format learning for internal knowledge sharing
        """
        internal_format = f"""Learning: {learning['title']}
Importance: {learning['importance']}/10
Source: {learning['source']}
Date: {learning['timestamp']}

Summary:
{self._create_summary(learning['content'])}

Full Details:
{learning['content']}

Tags: {', '.join(learning['tags']) if learning['tags'] else 'None'}

Recommended Actions:
- Consider implementing in upcoming projects
- Share with relevant teams
- Document in knowledge base
"""
        return internal_format
    
    def _format_for_documentation(self, learning: Dict) -> str:
        """
        Format learning for documentation integration
        """
        doc_format = f"""## {learning['title']}

**Category**: Learning/Insight
**Importance**: {learning['importance']}/10
**Date**: {learning['timestamp']}

{learning['content']}

**Tags**: {', '.join(learning['tags']) if learning['tags'] else 'None'}
"""
        return doc_format


def create_promotion_plan(formatted_learnings: List[Dict]) -> Dict[str, any]:
    """
    Create a plan for promoting learnings across channels
    """
    logger.info("Creating promotion plan...")
    
    plan = {
        'timestamp': datetime.datetime.now().isoformat(),
        'total_learnings': len(formatted_learnings),
        'by_channel': {
            'blog_posts': 0,
            'social_media': 0,
            'internal_sharing': 0,
            'documentation_updates': 0
        },
        'scheduled_promotions': [],
        'recommended_priority': []
    }
    
    for learning in formatted_learnings:
        importance = learning['importance']
        
        # Decide which channels to use based on importance
        if importance >= 9:
            # Very important: use all channels
            plan['by_channel']['blog_posts'] += 1
            plan['by_channel']['social_media'] += 1
            plan['by_channel']['internal_sharing'] += 1
            plan['by_channel']['documentation_updates'] += 1
            
            plan['recommended_priority'].append({
                'title': learning['title'],
                'channels': ['blog', 'social', 'internal', 'docs'],
                'urgency': 'high'
            })
        elif importance >= 7:
            # Moderately important: internal + docs
            plan['by_channel']['internal_sharing'] += 1
            plan['by_channel']['documentation_updates'] += 1
            
            plan['recommended_priority'].append({
                'title': learning['title'],
                'channels': ['internal', 'docs'],
                'urgency': 'medium'
            })
        else:
            # Lower importance: docs only
            plan['by_channel']['documentation_updates'] += 1
            
            plan['recommended_priority'].append({
                'title': learning['title'],
                'channels': ['docs'],
                'urgency': 'low'
            })
        
        # Add to scheduled promotions
        plan['scheduled_promotions'].append({
            'title': learning['title'],
            'importance': importance,
            'channels': learning['channels'].keys(),
            'scheduled_time': datetime.datetime.now().isoformat()
        })
    
    logger.info(f"Promotion plan created with {plan['total_learnings']} learnings")
    return plan


def execute_promotions(formatted_learnings: List[Dict], plan: Dict) -> List[str]:
    """
    Execute the promotions (placeholder - in real implementation would interact with APIs)
    """
    logger.info("Executing promotions...")
    
    results = []
    
    for learning in formatted_learnings:
        importance = learning['importance']
        
        # In a real implementation, this would:
        # - Publish blog posts
        # - Post to social media
        # - Share internally
        # - Update documentation
        # - Send notifications
        
        if importance >= 9:
            # High importance gets maximum promotion
            result = f"HIGH: Promoted '{learning['title']}' across all channels"
        elif importance >= 7:
            # Medium importance gets internal + docs promotion
            result = f"MEDIUM: Promoted '{learning['title']}' internally and in docs"
        else:
            # Low importance gets docs only
            result = f"LOW: Added '{learning['title']}' to documentation"
        
        results.append(result)
        logger.info(result)
    
    logger.info(f"Executed promotions for {len(results)} learnings")
    return results


def save_promotion_results(results: List[str], plan: Dict) -> str:
    """
    Save promotion results to a file
    """
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"reports/promotion_results_{timestamp}.md"
    
    # Ensure reports directory exists
    os.makedirs('reports', exist_ok=True)
    
    content = f"""Learning Promotion Results
========================
Execution Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
--------
Total Learnings Processed: {plan['total_learnings']}
Promotion Plan: {json.dumps(plan['by_channel'], indent=2)}

Results:
--------
{chr(10).join([f'- {result}' for result in results])}

Plan Details:
-------------
Priority Recommendations:
{chr(10).join([f'- {item["urgency"].upper()}: {item["title"]} ({", ".join(item["channels"])})' for item in plan['recommended_priority']])}
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Promotion results saved to {filename}")
    return filename


def main():
    """
    Main execution function
    """
    logger.info("Starting Learning Promotion Process")
    
    try:
        # Initialize learning promoter
        promoter = LearningPromoter()
        
        # Discover valuable learnings
        raw_learnings = promoter.discover_valuable_learnings()
        
        # Prioritize them
        prioritized_learnings = promoter.prioritize_learnings(raw_learnings)
        
        # Format for promotion
        formatted_learnings = [promoter.format_for_promotion(learning) for learning in prioritized_learnings[:10]]  # Limit to top 10
        
        # Create promotion plan
        plan = create_promotion_plan(formatted_learnings)
        
        # Execute promotions
        results = execute_promotions(formatted_learnings, plan)
        
        # Save results
        results_file = save_promotion_results(results, plan)
        
        logger.info(f"Learning Promotion completed successfully. Results: {results_file}")
        
        # Exit with success code
        return 0
        
    except Exception as e:
        logger.error(f"Error during Learning Promotion: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())