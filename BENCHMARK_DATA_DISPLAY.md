# Benchmark Data Display Implementation Guide

## Executive Summary
This document outlines the strategy for displaying underlying benchmark data (Mercer and Lattice) to HR users in the Salary Intelligence Platform. The goal is to provide transparency into salary calculations while maintaining a user-friendly interface.

## 1. Overview

The Salary Intelligence Platform uses multiple data sources to calculate competitive salary ranges:
- **Mercer Data**: Industry-standard compensation benchmarks
- **Lattice Data**: Modern tech company salary data
- **Internal Data**: Company-specific historical data (if available)

HR users need visibility into this data to:
- Validate salary recommendations
- Justify compensation decisions to stakeholders
- Understand market positioning
- Ensure pay equity compliance

## 2. Recommended UI Components

### 2.1 Benchmark Data Sources Panel

**Location**: Below the main salary range cards on the results page

**Visual Design**:
```
📊 Benchmark Data Sources
├── Mercer Data (3 matches)
│   ├── Software Engineer L5 - SF Bay Area
│   │   └── P25: $145K | P50: $165K | P75: $185K
│   ├── Senior Engineer - California Tech
│   │   └── P25: $140K | P50: $160K | P75: $180K
│   └── Data Date: Oct 2024 | Sample: 250 companies
│
└── Lattice Data (2 matches)
    ├── Senior SWE - San Francisco
    │   └── P25: $150K | P50: $170K | P75: $190K
    └── Data Date: Nov 2024 | Sample: 180 companies
```

### 2.2 Salary Calculation Breakdown

**Interactive Calculation Display**:
```
Base P50 (Market Data):        $165,000
├── Geographic Factor (1.4x):  +$66,000
├── Skills Premium (5%):       +$11,550
├── Market Adjustment:         +$5,000
└── Final Recommendation:      $247,550
```

### 2.3 Data Source Cards

Each benchmark source should display:
- **Provider Badge** (Mercer/Lattice with color coding)
- **Match Confidence** (percentage)
- **Data Freshness** (days since collection)
- **Sample Size** (number of companies)
- **Geographic Region**
- **Industry Segment**

## 3. Enhanced API Response Structure

### 3.1 New Endpoint: `/api/analysis/benchmarks/{job_id}`

**Response Format**:
```json
{
  "job_analysis": {
    "id": "uuid",
    "title": "Senior Software Engineer",
    "level": 5,
    "location": "San Francisco, CA"
  },
  "benchmark_sources": {
    "mercer": [
      {
        "id": "benchmark_uuid",
        "job_title": "Software Engineer V",
        "job_family": "Engineering",
        "location": "San Francisco, CA",
        "geography": "Bay Area",
        "level": 5,
        "band": 1,
        "zone": 1,
        "p10_salary": 125000,
        "p25_salary": 145000,
        "p50_salary": 165000,
        "p75_salary": 185000,
        "p90_salary": 210000,
        "mean_salary": 167500,
        "data_date": "2024-10-01",
        "company_count": 250,
        "employee_count": 5000,
        "industry": "Technology",
        "match_score": 0.95,
        "match_criteria": {
          "title_match": 0.90,
          "level_match": 1.00,
          "location_match": 1.00,
          "industry_match": 0.95
        }
      }
    ],
    "lattice": [
      {
        "id": "benchmark_uuid",
        "job_title": "Senior Software Engineer",
        "location": "San Francisco",
        "p25_salary": 150000,
        "p50_salary": 170000,
        "p75_salary": 190000,
        "data_date": "2024-11-01",
        "company_count": 180,
        "match_score": 0.92
      }
    ]
  },
  "calculation_methodology": {
    "base_calculation": {
      "method": "weighted_average",
      "weights": {
        "mercer": 0.6,
        "lattice": 0.4
      },
      "base_p25": 146500,
      "base_p50": 166500,
      "base_p75": 186500
    },
    "adjustments_applied": [
      {
        "type": "geographic",
        "factor": 1.4,
        "amount": 66600,
        "reason": "San Francisco premium vs national average"
      },
      {
        "type": "skills",
        "factor": 1.05,
        "amount": 11655,
        "reason": "AI/ML expertise premium"
      },
      {
        "type": "market_demand",
        "factor": 1.02,
        "amount": 4899,
        "reason": "High demand for senior engineers"
      }
    ],
    "final_calculation": {
      "min": 221802,
      "target": 249654,
      "max": 277506,
      "confidence_score": 0.95,
      "confidence_factors": {
        "data_points": 5,
        "data_freshness": "current",
        "match_quality": "excellent"
      }
    }
  },
  "market_context": {
    "percentile_in_market": 65,
    "competitive_position": "Above Market",
    "retention_risk": "Low",
    "talent_availability": "Moderate",
    "competing_companies": [
      "Google", "Meta", "Apple", "Amazon"
    ],
    "market_trend": "increasing",
    "yoy_change": "+5.2%"
  }
}
```

## 4. UI/UX Implementation Options

### Option A: Progressive Disclosure (Recommended)

**Default View**: Show summary only
```
💰 Recommended Salary: $249,654
   Based on 5 market data points | 95% confidence
   [▼ View Calculation Details]
```

**Expanded View**: Show full breakdown when clicked
- Benchmark data table
- Calculation steps
- Adjustment factors
- Source documents

### Option B: Tabbed Interface

```
[Summary] [Benchmark Data] [Calculation] [Market Analysis] [Export]
```

Each tab provides progressively more detail:
- **Summary**: Main salary recommendation
- **Benchmark Data**: Raw data from sources
- **Calculation**: Step-by-step breakdown
- **Market Analysis**: Competitive positioning
- **Export**: Download full report

### Option C: Side Panel Drawer

- Main results remain visible
- "View Sources" button opens right-side panel
- Panel contains scrollable detailed data
- Can be pinned open for reference

## 5. Data Display Requirements

### 5.1 Essential Information Per Benchmark

**Must Display**:
- Data source name and logo
- Job title matched
- All percentile values (P10, P25, P50, P75, P90)
- Geographic region
- Data collection date
- Sample size (companies and employees)
- Match confidence score

**Nice to Have**:
- Industry segment
- Company size distribution
- Years of experience range
- Education requirements
- Skills considered

### 5.2 Calculation Transparency

**Show Each Step**:
1. Base salary selection (which percentile used)
2. Geographic adjustment calculation
3. Skills premium application
4. Market demand factor
5. Final range determination
6. Confidence score calculation

### 5.3 Visual Indicators

**Use Color Coding**:
- 🟢 Green: High confidence matches (>90%)
- 🟡 Yellow: Moderate confidence (70-90%)
- 🔴 Red: Low confidence (<70%)

**Data Freshness Icons**:
- ✅ Current: <30 days old
- ⚠️ Recent: 30-90 days old
- ❌ Dated: >90 days old

## 6. Implementation Phases

### Phase 1: Basic Transparency (Week 1)
- Add benchmark count to existing UI
- Display confidence score
- Show data sources used (Mercer/Lattice)
- Add tooltip with basic calculation info

### Phase 2: Detailed View (Week 2)
- Implement expandable benchmark details section
- Create calculation breakdown component
- Add data freshness indicators
- Include sample size information

### Phase 3: Advanced Features (Week 3-4)
- Interactive comparison table
- Export to PDF/Excel
- Historical trending graphs
- Custom benchmark upload interface

## 7. Backend Requirements

### 7.1 Database Query Enhancements

```python
# Return individual benchmark records, not just aggregates
def get_benchmark_details(job_analysis_id):
    return {
        'benchmarks': fetch_matching_benchmarks(),
        'calculation_audit': track_calculation_steps(),
        'metadata': include_source_metadata()
    }
```

### 7.2 New Service Methods

```python
class BenchmarkService:
    def get_benchmark_sources(self, job_analysis_id: str):
        """Return all benchmark data used in calculation"""

    def get_calculation_breakdown(self, job_analysis_id: str):
        """Return step-by-step calculation details"""

    def get_match_scoring(self, job_analysis_id: str):
        """Return how well each benchmark matches the job"""
```

## 8. Benefits for HR Users

### 8.1 Trust and Transparency
- See exact data sources
- Understand calculation methodology
- Validate recommendations independently

### 8.2 Decision Support
- Justify offers to candidates
- Defend compensation to leadership
- Document pay equity compliance

### 8.3 Negotiation Preparation
- Understand range flexibility
- Know market positioning
- See competitive landscape

### 8.4 Learning and Insights
- Learn market dynamics
- Identify talent trends
- Spot compensation gaps

## 9. Technical Considerations

### 9.1 Performance
- Cache benchmark queries (Redis)
- Lazy load detailed data
- Paginate large result sets

### 9.2 Security
- Mask sensitive company names in benchmarks
- Aggregate data where necessary
- Audit log access to detailed data

### 9.3 Scalability
- Design for future data sources
- Support custom benchmarks
- Allow filtering and sorting

## 10. Success Metrics

### 10.1 User Engagement
- Click-through rate on "View Details"
- Time spent reviewing benchmark data
- Export/download frequency

### 10.2 Business Value
- Reduction in compensation questions
- Faster offer approval process
- Improved offer acceptance rates

### 10.3 Data Quality
- Benchmark match scores
- Confidence score distribution
- Data freshness metrics

## 11. Future Enhancements

### 11.1 Advanced Analytics
- Predictive salary trends
- Retention risk modeling
- Competitive intelligence dashboard

### 11.2 Customization
- Custom benchmark uploads
- Industry-specific adjustments
- Company-specific factors

### 11.3 Integration
- HRIS system connections
- ATS integration
- Compensation planning tools

## 12. Conclusion

Displaying benchmark data transparently is crucial for HR users to trust and effectively use the Salary Intelligence Platform. This implementation guide provides a roadmap for progressively enhancing the platform's transparency while maintaining usability.

The recommended approach is to start with basic transparency features and progressively add more detailed views based on user feedback and needs. This ensures the platform remains both powerful and approachable for all skill levels of HR professionals.

---

**Document Version**: 1.0
**Last Updated**: November 2024
**Next Review**: January 2025