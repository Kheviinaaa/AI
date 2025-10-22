# Test Strategy & Plan
## AI-Powered Jira Agent

*Note: All test artifacts consolidated in /test folder*

### 1. Test Objectives
- Validate AI-generated stories and test cases meet quality standards
- Ensure system handles both Jira API and mock data sources  
- Verify exports (JSON/CSV) are correct and complete
- Confirm risk-based test coverage for high-risk stories
- Validate system reliability and error handling

### 2. Test Levels
- **Unit Tests**: `/test/unit/` - Schema validation, formatters, utilities
- **Integration Tests**: `/test/integration/` - API endpoints with AI & Jira
- **E2E Tests**: `/test/e2e/` - Complete user journey through UI
- **Acceptance Tests**: Baseline comparison against golden outputs

### 3. Test Scope
**In Scope:**
- AI story generation output validation
- Test case generation quality
- JSON/CSV export functionality
- Jira API integration (with fixtures)
- Web UI basic functionality
- Error handling and resilience

**Out of Scope:**
- Performance load testing (beyond basic timing)
- Security penetration testing
- Cross-browser compatibility
- Mobile responsiveness

### 4. Entry Criteria
- Development environment running on localhost:5000
- Mock epic data available in `/test/data/`
- AI schemas defined in `/src/schemas/`
- Dependencies installed (pytest, requests, jsonschema)

### 5. Exit Criteria
- All critical/high severity defects resolved
- ≥95% schema validity rate
- 100% risk coverage for high-risk stories
- 100% export success rate
- Metrics report generated and reviewed
- All automated tests passing

### 6. Test Environment
- **URL**: http://localhost:5000
- **API Base**: http://localhost:5000/api
- **Test Data**: `/test/data/` directory
- **Tools**: pytest, requests, jsonschema

### 7. Risk Assessment
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| AI output quality inconsistency | High | Medium | Baseline comparison, schema validation |
| Jira API reliability | Medium | High | Mock fixtures, error handling tests |
| Schema changes breaking tests | High | Low | Schema versioning, isolated validation |
| Performance degradation | Medium | Low | Basic timing checks in evaluation |

### 8. Suspension & Resumption Criteria
**Suspend testing if:**
- AI service unavailable for >30 minutes
- Critical schema changes deployed
- >50% of tests failing due to environment issues
- Jira API rate limits exceeded

**Resume testing when:**
- Dependencies stable and available
- Critical defects resolved
- Environment restored and verified

### 9. Test Automation Strategy
- **Framework**: pytest
- **CI Integration**: Run on every PR to dev branch
- **Reporting**: Automated metrics in `/test/docs/testing-report.md`
- **Coverage**: Unit 100%, Integration 90%, E2E 70%

### 10. Defect Management
- **Tool**: `/test/docs/defects.csv` and/or GitHub Issues
- **Severity Levels**: Blocker, Critical, Major, Minor
- **Workflow**: Log → Assign → Fix → Retest → Close
- **Traceability**: Link defects to failing tests

### 11. Metrics & Reporting
| Metric | Target | Measurement |
|--------|--------|-------------|
| Structural Validity | ≥95% | Schema validation passes |
| Completeness | 100% | Stories/tests within constraints |
| Risk Coverage | 100% | High-risk stories meet rules |
| Export Success | 100% | CSV+JSON generated without errors |
| Test Pass Rate | ≥95% | Automated test execution |

### 12. Responsibilities
- **Test Engineer**: Implement and maintain all test artifacts
- **AI Team**: Fix schema and generation issues
- **Backend Team**: Fix API and export issues
- **All Teams**: Review and act on test reports
