#!/bin/bash
# 01-session-lifecycle.sh — Contract tests for session resource
set -euo pipefail

source "$(dirname "$0")/../lib/test-helpers.sh"

# -- Tests --

test_session_create() {
  OUTPUT=$("$ARBITRATOR" session create \
    --playbook interview \
    --team-lead interview \
    --user testuser \
    --machine testhost)
  SESSION_ID=$(echo "$OUTPUT" | jq -r '.session_id')
  assert_not_empty "$SESSION_ID" "session_id"
}

test_session_get() {
  OUTPUT=$("$ARBITRATOR" session create \
    --playbook generate \
    --team-lead analysis \
    --user alice \
    --machine devbox)
  SESSION_ID=$(echo "$OUTPUT" | jq -r '.session_id')

  OUTPUT=$("$ARBITRATOR" session get --session "$SESSION_ID")
  assert_json_field "$OUTPUT" ".playbook" "generate"
  assert_json_field "$OUTPUT" ".team_lead" "analysis"
  assert_json_field "$OUTPUT" ".user" "alice"
  assert_json_field "$OUTPUT" ".machine" "devbox"
  assert_json_not_empty "$OUTPUT" ".creation_date" "creation_date"
}

test_session_list_by_playbook() {
  "$ARBITRATOR" session create --playbook lint --team-lead audit --user bob --machine ci > /dev/null
  "$ARBITRATOR" session create --playbook lint --team-lead audit --user bob --machine ci > /dev/null
  "$ARBITRATOR" session create --playbook interview --team-lead interview --user bob --machine ci > /dev/null

  OUTPUT=$("$ARBITRATOR" session list --playbook lint)
  COUNT=$(echo "$OUTPUT" | jq 'length')
  [[ "$COUNT" -ge 2 ]] || { echo "expected at least 2 lint sessions, got ${COUNT}" >&2; return 1; }
}

test_session_list_empty() {
  OUTPUT=$("$ARBITRATOR" session list --playbook nonexistent)
  assert_json_count "$OUTPUT" "0" "no sessions should match"
}

test_session_add_path() {
  OUTPUT=$("$ARBITRATOR" session create \
    --playbook interview \
    --team-lead interview \
    --user testuser \
    --machine testhost)
  SESSION_ID=$(echo "$OUTPUT" | jq -r '.session_id')

  OUTPUT=$("$ARBITRATOR" session add-path \
    --session "$SESSION_ID" \
    --path /tmp/test-repo \
    --type repo)
  assert_json_field "$OUTPUT" ".type" "repo"
  assert_json_field "$OUTPUT" ".path" "/tmp/test-repo"
}

test_session_get_nonexistent() {
  if "$ARBITRATOR" session get --session "nonexistent-id" 2>/dev/null; then
    echo "expected failure for nonexistent session" >&2
    return 1
  fi
}

test_session_create_missing_flags() {
  if "$ARBITRATOR" session create --playbook interview 2>/dev/null; then
    echo "expected failure for missing flags" >&2
    return 1
  fi
}

# -- Run --

run_test "session create returns session_id" test_session_create
run_test "session get returns all fields" test_session_get
run_test "session list filters by playbook" test_session_list_by_playbook
run_test "session list returns empty for no matches" test_session_list_empty
run_test "session add-path stores path" test_session_add_path
run_test "session get fails for nonexistent session" test_session_get_nonexistent
run_test "session create fails with missing flags" test_session_create_missing_flags

test_summary
