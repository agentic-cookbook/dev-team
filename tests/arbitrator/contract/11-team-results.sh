#!/bin/bash
# 11-team-results.sh — Contract tests for team-result resource
set -euo pipefail

source "$(dirname "$0")/../lib/test-helpers.sh"

# -- Setup --

make_session() {
  "$ARBITRATOR" session create \
    --playbook generate \
    --team-lead review \
    --user testuser \
    --machine testhost \
    | jq -r '.session_id'
}

make_result() {
  local session_id="$1" specialist="$2"
  "$ARBITRATOR" result create \
    --session "$session_id" \
    --specialist "$specialist" \
    | jq -r '.result_id'
}

# -- Tests --

test_team_result_create_returns_id() {
  SESSION_ID=$(make_session)
  RESULT_ID=$(make_result "$SESSION_ID" "security")

  OUTPUT=$("$ARBITRATOR" team-result create \
    --session "$SESSION_ID" \
    --result "$RESULT_ID" \
    --specialist security \
    --team authentication)
  TR_ID=$(echo "$OUTPUT" | jq -r '.team_result_id')
  assert_not_empty "$TR_ID" "team_result_id"
}

test_team_result_create_sets_running_status() {
  SESSION_ID=$(make_session)
  RESULT_ID=$(make_result "$SESSION_ID" "security")

  "$ARBITRATOR" team-result create \
    --session "$SESSION_ID" \
    --result "$RESULT_ID" \
    --specialist security \
    --team authorization > /dev/null

  OUTPUT=$("$ARBITRATOR" team-result get \
    --session "$SESSION_ID" \
    --specialist security \
    --team authorization)
  assert_json_field "$OUTPUT" '.status' "running"
  assert_json_field "$OUTPUT" '.iteration' "0"
  assert_json_field "$OUTPUT" '.specialist' "security"
  assert_json_field "$OUTPUT" '.team_name' "authorization"
}

test_team_result_update_status_and_iteration() {
  SESSION_ID=$(make_session)
  RESULT_ID=$(make_result "$SESSION_ID" "security")

  "$ARBITRATOR" team-result create \
    --session "$SESSION_ID" \
    --result "$RESULT_ID" \
    --specialist security \
    --team token-handling > /dev/null

  "$ARBITRATOR" team-result update \
    --session "$SESSION_ID" \
    --specialist security \
    --team token-handling \
    --status passed \
    --iteration 2 > /dev/null

  OUTPUT=$("$ARBITRATOR" team-result get \
    --session "$SESSION_ID" \
    --specialist security \
    --team token-handling)
  assert_json_field "$OUTPUT" '.status' "passed"
  assert_json_field "$OUTPUT" '.iteration' "2"
}

test_team_result_update_verifier_feedback() {
  SESSION_ID=$(make_session)
  RESULT_ID=$(make_result "$SESSION_ID" "security")

  "$ARBITRATOR" team-result create \
    --session "$SESSION_ID" \
    --result "$RESULT_ID" \
    --specialist security \
    --team cors > /dev/null

  "$ARBITRATOR" team-result update \
    --session "$SESSION_ID" \
    --specialist security \
    --team cors \
    --status failed \
    --iteration 1 \
    --verifier-feedback "Missing CORS allowlist check" > /dev/null

  OUTPUT=$("$ARBITRATOR" team-result get \
    --session "$SESSION_ID" \
    --specialist security \
    --team cors)
  assert_json_field "$OUTPUT" '.status' "failed"
  assert_json_field "$OUTPUT" '.verifier_feedback' "Missing CORS allowlist check"
}

test_team_result_list_all_for_specialist() {
  SESSION_ID=$(make_session)
  RESULT_ID=$(make_result "$SESSION_ID" "security")

  "$ARBITRATOR" team-result create --session "$SESSION_ID" --result "$RESULT_ID" --specialist security --team authentication > /dev/null
  "$ARBITRATOR" team-result create --session "$SESSION_ID" --result "$RESULT_ID" --specialist security --team authorization > /dev/null
  "$ARBITRATOR" team-result create --session "$SESSION_ID" --result "$RESULT_ID" --specialist security --team cors > /dev/null

  OUTPUT=$("$ARBITRATOR" team-result list --session "$SESSION_ID" --specialist security)
  assert_json_count "$OUTPUT" "3" "should have 3 team-results for security"
}

test_team_result_list_filters_by_status() {
  SESSION_ID=$(make_session)
  RESULT_ID=$(make_result "$SESSION_ID" "security")

  "$ARBITRATOR" team-result create --session "$SESSION_ID" --result "$RESULT_ID" --specialist security --team authentication > /dev/null
  "$ARBITRATOR" team-result create --session "$SESSION_ID" --result "$RESULT_ID" --specialist security --team authorization > /dev/null

  "$ARBITRATOR" team-result update --session "$SESSION_ID" --specialist security --team authentication --status passed --iteration 1 > /dev/null

  OUTPUT=$("$ARBITRATOR" team-result list --session "$SESSION_ID" --specialist security --status passed)
  assert_json_count "$OUTPUT" "1" "should have 1 passed team-result"
  assert_json_field "$OUTPUT" '.[0].team_name' "authentication"
}

test_team_result_list_filters_by_specialist() {
  SESSION_ID=$(make_session)
  SEC_RESULT=$(make_result "$SESSION_ID" "security")
  ACC_RESULT=$(make_result "$SESSION_ID" "accessibility")

  "$ARBITRATOR" team-result create --session "$SESSION_ID" --result "$SEC_RESULT" --specialist security --team authentication > /dev/null
  "$ARBITRATOR" team-result create --session "$SESSION_ID" --result "$ACC_RESULT" --specialist accessibility --team accessibility > /dev/null

  OUTPUT=$("$ARBITRATOR" team-result list --session "$SESSION_ID" --specialist security)
  assert_json_count "$OUTPUT" "1" "should have 1 team-result for security"
}

test_team_result_list_empty_session() {
  SESSION_ID=$(make_session)

  OUTPUT=$("$ARBITRATOR" team-result list --session "$SESSION_ID")
  assert_json_count "$OUTPUT" "0" "should have 0 team-results"
}

test_team_result_get_nonexistent_fails() {
  SESSION_ID=$(make_session)
  make_result "$SESSION_ID" "security" > /dev/null

  if "$ARBITRATOR" team-result get --session "$SESSION_ID" --specialist security --team nonexistent 2>/dev/null; then
    echo "Expected failure for nonexistent team-result" >&2
    return 1
  fi
}

test_team_result_update_nonexistent_fails() {
  SESSION_ID=$(make_session)
  make_result "$SESSION_ID" "security" > /dev/null

  if "$ARBITRATOR" team-result update --session "$SESSION_ID" --specialist security --team nonexistent --status passed 2>/dev/null; then
    echo "Expected failure for nonexistent team-result" >&2
    return 1
  fi
}

# -- Run --

run_test "team-result create returns team_result_id" test_team_result_create_returns_id
run_test "team-result create sets running status and iteration 0" test_team_result_create_sets_running_status
run_test "team-result update changes status and iteration" test_team_result_update_status_and_iteration
run_test "team-result update stores verifier feedback" test_team_result_update_verifier_feedback
run_test "team-result list returns all for specialist" test_team_result_list_all_for_specialist
run_test "team-result list filters by status" test_team_result_list_filters_by_status
run_test "team-result list filters by specialist" test_team_result_list_filters_by_specialist
run_test "team-result list returns empty for new session" test_team_result_list_empty_session
run_test "team-result get nonexistent fails" test_team_result_get_nonexistent_fails
run_test "team-result update nonexistent fails" test_team_result_update_nonexistent_fails

test_summary
