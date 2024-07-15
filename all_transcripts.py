from transcripts import (
    critical_security_bug,
    minor_bug,
    no_issues,
    similar_bug_one,
    similar_bug_two,
    similar_feature_one,
    similar_feature_two,
    single_feature_request
)

transcript_registry = {
    'critical_security_bug': critical_security_bug.TRANSCRIPT,
    'minor_bug': minor_bug.TRANSCRIPT,
    'no_issues': no_issues.TRANSCRIPT,
    'similar_bug_one': similar_bug_one.TRANSCRIPT,
    'similar_bug_two': similar_bug_two.TRANSCRIPT,
    'similar_feature_one': similar_feature_one.TRANSCRIPT,
    'similar_feature_two': similar_feature_two.TRANSCRIPT,
    'single_feature_request': single_feature_request.TRANSCRIPT,
}
