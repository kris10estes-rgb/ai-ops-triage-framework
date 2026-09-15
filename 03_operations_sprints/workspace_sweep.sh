#!/usr/bin/env bash
#
# workspace_sweep.sh — Find, list, and summarize Markdown files in this workspace
# so people and AI agents can decide what is worth loading into context.
#
# Token counts are estimates (bytes ÷ CHARS_PER_TOKEN). Real tokenizers vary by
# model and language, so treat the numbers as relative sizes, not billing figures.
#
# Works with macOS (bash 3.2, BSD tools) and Linux (GNU tools).
# Run with -h for usage.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROG="$(basename "$0")"

ROOT="$(dirname "$SCRIPT_DIR")"
TOP_N=10
WARN_TOKENS=4000
FORMAT="text"
OUTPUT=""
SHOW_OUTLINE=0
EXCERPT_CHARS=160
CHARS_PER_TOKEN="${CHARS_PER_TOKEN:-4}"
EXCLUDES=(.git node_modules .venv venv dist build .next __pycache__ .cache .pytest_cache archive)
INCLUDE_ARCHIVE=0
# Generated index files are never counted as workspace documents.
INDEX_NAME="CONTEXT_INDEX.md"

die() {
  echo "$PROG: $*" >&2
  exit 1
}

usage() {
  cat <<EOF
Usage: $PROG [options]

Find, list, and summarize Markdown files (.md, .markdown, .mdx) to optimize AI context usage.

Options:
  -r DIR     Root directory to scan (default: workspace root, $ROOT)
  -n NUM     Number of largest files to highlight (default: $TOP_N; 0 hides the section)
  -w TOKENS  Flag files with more estimated tokens than this (default: $WARN_TOKENS)
  -x NAME    Exclude directories with this name (repeatable)
             Excluded by default: ${EXCLUDES[*]}
  -a         Include archive/ directories (superseded documents)
  -s         Include a heading outline (H1–H3) for each file
  -m         Output Markdown instead of plain text
  -o FILE    Write the report to FILE instead of stdout (FILE is left out of the scan)
  -h         Show this help

Files named $INDEX_NAME are always skipped, since they are generated reports.

Environment:
  CHARS_PER_TOKEN  Characters per token used for estimates (default: 4)

Examples:
  $PROG                          # Summary of the whole workspace
  $PROG -s -n 5                  # Include outlines; show top 5 largest files
  $PROG -m -o CONTEXT_INDEX.md   # Write a compact index agents can read first
EOF
}

is_uint() {
  [[ "$1" =~ ^[0-9]+$ ]]
}

# 1234567 -> 1,234,567
fmt_num() {
  local n="$1" out=""
  while (( ${#n} > 3 )); do
    out=",${n: -3}${out}"
    n="${n:0:${#n}-3}"
  done
  printf '%s%s' "$n" "$out"
}

# Share of total tokens with one decimal place, e.g. 12.5
percent() {
  local part="$1" tenths=0
  if (( TOTAL_TOKENS > 0 )); then
    tenths=$(( part * 1000 / TOTAL_TOKENS ))
  fi
  printf '%d.%d' $(( tenths / 10 )) $(( tenths % 10 ))
}

# plural 1 file -> "1 file", plural 3 file -> "3 files"
plural() {
  if [[ "$1" == "1" ]]; then
    printf '%s %s' "$(fmt_num "$1")" "$2"
  else
    printf '%s %ss' "$(fmt_num "$1")" "$2"
  fi
}

truncate_text() {
  local s="$1" max="$2"
  if (( ${#s} > max )); then
    printf '%s…' "${s:0:max-1}"
  else
    printf '%s' "$s"
  fi
}

md_escape() {
  printf '%s' "$1" | sed 's/|/\\|/g'
}

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------

while getopts ":r:n:w:x:o:asmh" opt; do
  case "$opt" in
    r) ROOT="$OPTARG" ;;
    n) TOP_N="$OPTARG" ;;
    w) WARN_TOKENS="$OPTARG" ;;
    x) EXCLUDES+=("$OPTARG") ;;
    o) OUTPUT="$OPTARG" ;;
    a) INCLUDE_ARCHIVE=1 ;;
    s) SHOW_OUTLINE=1 ;;
    m) FORMAT="markdown" ;;
    h) usage; exit 0 ;;
    :) die "option -$OPTARG requires an argument (see -h)" ;;
    \?) die "unknown option -$OPTARG (see -h)" ;;
  esac
done
shift $(( OPTIND - 1 ))
if (( $# > 0 )); then
  die "unexpected argument: $1 (see -h)"
fi

[[ -d "$ROOT" ]] || die "root directory not found: $ROOT"
is_uint "$TOP_N" || die "-n must be a non-negative integer"
is_uint "$WARN_TOKENS" || die "-w must be a non-negative integer"
if ! is_uint "$CHARS_PER_TOKEN" || (( CHARS_PER_TOKEN == 0 )); then
  die "CHARS_PER_TOKEN must be a positive integer"
fi

ROOT="$(cd "$ROOT" && pwd)"

OUTPUT_ABS=""
if [[ -n "$OUTPUT" ]]; then
  out_dir="$(dirname "$OUTPUT")"
  [[ -d "$out_dir" ]] || die "output directory not found: $out_dir"
  OUTPUT_ABS="$(cd "$out_dir" && pwd)/$(basename "$OUTPUT")"
fi

# ---------------------------------------------------------------------------
# Discover files
# ---------------------------------------------------------------------------

if (( INCLUDE_ARCHIVE )); then
  kept=()
  for name in "${EXCLUDES[@]}"; do
    if [[ "$name" != "archive" ]]; then
      kept+=("$name")
    fi
  done
  EXCLUDES=("${kept[@]}")
fi

prune_expr=()
for name in "${EXCLUDES[@]}"; do
  if (( ${#prune_expr[@]} > 0 )); then
    prune_expr+=(-o)
  fi
  prune_expr+=(-name "$name")
done

FILES=()
while IFS= read -r -d '' f; do
  if [[ "$f" != "$OUTPUT_ABS" && "$(basename "$f")" != "$INDEX_NAME" ]]; then
    FILES+=("$f")
  fi
done < <(
  find "$ROOT" -mindepth 1 \
    -type d \( "${prune_expr[@]}" \) -prune -o \
    -type f \( -iname '*.md' -o -iname '*.markdown' -o -iname '*.mdx' \) -print0 |
    sort -z
)

if (( ${#FILES[@]} == 0 )); then
  echo "$PROG: no Markdown files found under $ROOT" >&2
  exit 0
fi

# ---------------------------------------------------------------------------
# Analyze files
# ---------------------------------------------------------------------------

# One pass per file. Skips YAML front matter and fenced code blocks, and emits:
#   O<TAB>level<TAB>heading   for H1–H3 headings (outline)
#   T<TAB>title               first H1, else front-matter title
#   E<TAB>excerpt             first line of prose, plus up to 3 list items if it ends with ":"
#   H<TAB>count               total headings
AWK_PROG='
{ sub(/\r$/, "") }
NR == 1 && /^---[ \t]*$/ { in_fm = 1; next }
in_fm {
  if ($0 ~ /^---[ \t]*$/) {
    in_fm = 0
  } else if (fm_title == "" && $0 ~ /^title:/) {
    t = $0
    sub(/^title:[ \t]*/, "", t)
    gsub(/^["\047]|["\047]$/, "", t)
    fm_title = t
  }
  next
}
/^[ \t]*(```|~~~)/ { in_code = !in_code; want_list = 0; next }
in_code { next }
/^#+[ \t]/ {
  want_list = 0
  match($0, /^#+/)
  level = RLENGTH
  text = substr($0, level + 1)
  sub(/^[ \t]+/, "", text)
  sub(/[ \t]+#+[ \t]*$/, "", text)
  sub(/[ \t]+$/, "", text)
  headings++
  if (level == 1 && title == "") title = text
  if (level <= 3) print "O\t" level "\t" text
  next
}
want_list {
  line = $0
  sub(/^[ \t]+/, "", line)
  if (line == "") next
  if (line ~ /^([-*+]|[0-9]+\.)[ \t]+/) {
    sub(/^([-*+]|[0-9]+\.)[ \t]+/, "", line)
    gsub(/\*\*|__|`/, "", line)
    sub(/[.;][ \t]*$/, "", line)
    excerpt = excerpt (list_items == 0 ? " " : "; ") line
    list_items++
    if (list_items >= 3) want_list = 0
    next
  }
  want_list = 0
}
excerpt == "" {
  line = $0
  sub(/^[ \t]+/, "", line)
  if (line == "" || line ~ /^(\||<|---|\*\*\*|___|===|!\[)/) next
  sub(/^([-*+>]|[0-9]+\.)[ \t]+/, "", line)
  gsub(/\*\*|__|`/, "", line)
  sub(/[ \t]+$/, "", line)
  excerpt = line
  # An intro that ends with a colon usually introduces a list; pull in its first items.
  if (excerpt ~ /:$/) want_list = 1
  next
}
END {
  if (title == "") title = fm_title
  print "T\t" title
  print "E\t" excerpt
  print "H\t" (headings + 0)
}'

F_REL=() F_LINES=() F_WORDS=() F_BYTES=() F_TOKENS=() F_MTIME=()
F_TITLE=() F_EXCERPT=() F_HEADINGS=() F_OUTLINE=() F_OUTLINE_MIN=() F_HASH=()
TOTAL_LINES=0 TOTAL_WORDS=0 TOTAL_BYTES=0 TOTAL_TOKENS=0
OVER_IDX="" EMPTY_IDX=""

for (( i = 0; i < ${#FILES[@]}; i++ )); do
  f="${FILES[$i]}"

  read -r lines words bytes < <(wc -l -w -c < "$f")
  tokens=$(( (bytes + CHARS_PER_TOKEN - 1) / CHARS_PER_TOKEN ))

  title="" excerpt="" headings=0 outline="" outline_min=1
  while IFS=$'\t' read -r kind a b; do
    case "$kind" in
      T) title="$a" ;;
      E) excerpt="$a" ;;
      H) headings="$a" ;;
      O)
        if [[ -z "$outline" ]] || (( a < outline_min )); then
          outline_min=$a
        fi
        outline+="${a}"$'\t'"${b}"$'\n'
        ;;
    esac
  done < <(awk "$AWK_PROG" "$f")

  if [[ -z "$title" ]]; then
    title="$(basename "$f")"
  fi

  F_REL[$i]="${f#"$ROOT"/}"
  F_LINES[$i]=$lines
  F_WORDS[$i]=$words
  F_BYTES[$i]=$bytes
  F_TOKENS[$i]=$tokens
  F_MTIME[$i]="$(date -r "$f" '+%Y-%m-%d' 2>/dev/null || echo 'unknown')"
  F_TITLE[$i]="$title"
  F_EXCERPT[$i]="$(truncate_text "$excerpt" "$EXCERPT_CHARS")"
  F_HEADINGS[$i]=$headings
  F_OUTLINE[$i]="$outline"
  F_OUTLINE_MIN[$i]=$outline_min
  F_HASH[$i]="$(cksum < "$f" | awk '{ print $1 "-" $2 }')"

  TOTAL_LINES=$(( TOTAL_LINES + lines ))
  TOTAL_WORDS=$(( TOTAL_WORDS + words ))
  TOTAL_BYTES=$(( TOTAL_BYTES + bytes ))
  TOTAL_TOKENS=$(( TOTAL_TOKENS + tokens ))

  if (( words == 0 )); then
    EMPTY_IDX+="$i "
  elif (( tokens > WARN_TOKENS )); then
    OVER_IDX+="$i "
  fi
done

# File indexes sorted by estimated tokens, largest first
SORTED_IDX="$(
  for (( i = 0; i < ${#FILES[@]}; i++ )); do
    printf '%s %s\n' "${F_TOKENS[$i]}" "$i"
  done | sort -k1,1nr -k2,2n | awk '{ print $2 }'
)"
TOP_IDX="$(printf '%s\n' "$SORTED_IDX" | awk -v n="$TOP_N" 'NR <= n')"
TOP3_TOKENS="$(
  for idx in $(printf '%s\n' "$SORTED_IDX" | awk 'NR <= 3'); do
    printf '%s\n' "${F_TOKENS[$idx]}"
  done | awk '{ s += $1 } END { print s + 0 }'
)"

# Groups of non-empty files with identical content, one tab-separated group per line
DUPES="$(
  for (( i = 0; i < ${#FILES[@]}; i++ )); do
    if (( F_WORDS[i] > 0 )); then
      printf '%s\t%s\n' "${F_HASH[$i]}" "${F_REL[$i]}"
    fi
  done | sort | awk -F '\t' '
    $1 == prev { group = group "\t" $2; n++; next }
    { if (n > 1) print group; group = $2; n = 1; prev = $1 }
    END { if (n > 1) print group }
  '
)"

GENERATED="$(date '+%Y-%m-%d %H:%M %Z')"

# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

render_text() {
  local i idx lvl text group
  local -a parts

  echo "WORKSPACE SWEEP"
  echo "==============="
  printf 'Root:         %s\n' "$ROOT"
  printf 'Generated:    %s\n' "$GENERATED"
  printf 'Files:        %s\n' "$(plural "${#FILES[@]}" 'Markdown file')"
  printf 'Size:         %s lines · %s words · %s bytes\n' \
    "$(fmt_num "$TOTAL_LINES")" "$(fmt_num "$TOTAL_WORDS")" "$(fmt_num "$TOTAL_BYTES")"
  printf 'Est. tokens:  ~%s (%s chars/token)\n' "$(fmt_num "$TOTAL_TOKENS")" "$CHARS_PER_TOKEN"

  echo
  echo "FILES"
  printf '  %9s %7s %8s  %-10s  %s\n' "~TOKENS" "LINES" "WORDS" "MODIFIED" "PATH"
  for (( i = 0; i < ${#FILES[@]}; i++ )); do
    printf '  %9s %7s %8s  %-10s  %s\n' \
      "$(fmt_num "${F_TOKENS[$i]}")" "$(fmt_num "${F_LINES[$i]}")" \
      "$(fmt_num "${F_WORDS[$i]}")" "${F_MTIME[$i]}" "${F_REL[$i]}"
  done

  if (( TOP_N > 0 )); then
    echo
    echo "LARGEST FILES (top $TOP_N by estimated tokens)"
    for idx in $TOP_IDX; do
      printf '  %9s  %5s%%  %s\n' \
        "$(fmt_num "${F_TOKENS[$idx]}")" "$(percent "${F_TOKENS[$idx]}")" "${F_REL[$idx]}"
    done
  fi

  echo
  echo "FLAGS"
  if [[ -z "$OVER_IDX$EMPTY_IDX$DUPES" ]]; then
    echo "  None: no oversized, empty, or duplicate files."
  fi
  if [[ -n "$OVER_IDX" ]]; then
    echo "  Over ~$(fmt_num "$WARN_TOKENS") tokens:"
    for idx in $OVER_IDX; do
      printf '    - %s (~%s tokens)\n' "${F_REL[$idx]}" "$(fmt_num "${F_TOKENS[$idx]}")"
    done
  fi
  if [[ -n "$EMPTY_IDX" ]]; then
    echo "  Empty (no words):"
    for idx in $EMPTY_IDX; do
      printf '    - %s\n' "${F_REL[$idx]}"
    done
  fi
  if [[ -n "$DUPES" ]]; then
    echo "  Identical content:"
    while IFS= read -r group; do
      IFS=$'\t' read -r -a parts <<< "$group"
      printf '    - %s\n' "${parts[0]}"
      for (( i = 1; i < ${#parts[@]}; i++ )); do
        printf '      = %s\n' "${parts[$i]}"
      done
    done <<< "$DUPES"
  fi

  echo
  echo "SUMMARIES"
  for (( i = 0; i < ${#FILES[@]}; i++ )); do
    echo "  ${F_REL[$i]}"
    printf '    Title:    %s\n' "${F_TITLE[$i]}"
    if [[ -n "${F_EXCERPT[$i]}" ]]; then
      printf '    Summary:  %s\n' "${F_EXCERPT[$i]}"
    fi
    printf '    Shape:    ~%s · %s · %s\n' "$(plural "${F_TOKENS[$i]}" token)" \
      "$(plural "${F_LINES[$i]}" line)" "$(plural "${F_HEADINGS[$i]}" heading)"
    if (( SHOW_OUTLINE )) && [[ -n "${F_OUTLINE[$i]}" ]]; then
      echo "    Outline:"
      while IFS=$'\t' read -r lvl text; do
        if [[ -n "$lvl" ]]; then
          printf '      %*s- %s\n' $(( (lvl - F_OUTLINE_MIN[i]) * 2 )) "" "$text"
        fi
      done <<< "${F_OUTLINE[$i]}"
    fi
    echo
  done

  echo "CONTEXT TIPS"
  if (( ${#FILES[@]} > 3 && TOTAL_TOKENS > 0 )); then
    printf '  - The 3 largest files hold %s%% of estimated tokens. Check those first when trimming.\n' \
      "$(percent "$TOP3_TOKENS")"
  fi
  if [[ -n "$OVER_IDX" ]]; then
    echo "  - Load oversized files by section instead of whole (use -s for outlines), or split them."
  fi
  if [[ -n "$EMPTY_IDX" ]]; then
    echo "  - Fill in or delete empty files so they don't clutter search results."
  fi
  if [[ -n "$DUPES" ]]; then
    echo "  - Keep one copy of identical files and link to it from the others."
  fi
  echo "  - Give agents a compact index to read first: $PROG -m -o CONTEXT_INDEX.md"
}

render_markdown() {
  local i idx lvl text group
  local -a parts

  echo "# Workspace Sweep"
  echo
  echo "| | |"
  echo "|---|---|"
  echo "| Root | \`$ROOT\` |"
  echo "| Generated | $GENERATED |"
  echo "| Files | $(plural "${#FILES[@]}" 'Markdown file') |"
  echo "| Size | $(fmt_num "$TOTAL_LINES") lines · $(fmt_num "$TOTAL_WORDS") words · $(fmt_num "$TOTAL_BYTES") bytes |"
  echo "| Est. tokens | ~$(fmt_num "$TOTAL_TOKENS") ($CHARS_PER_TOKEN chars/token) |"

  echo
  echo "## Files"
  echo
  echo "| Path | Title | ~Tokens | Lines | Modified |"
  echo "|---|---|--:|--:|---|"
  for (( i = 0; i < ${#FILES[@]}; i++ )); do
    echo "| \`$(md_escape "${F_REL[$i]}")\` | $(md_escape "${F_TITLE[$i]}") | $(fmt_num "${F_TOKENS[$i]}") | $(fmt_num "${F_LINES[$i]}") | ${F_MTIME[$i]} |"
  done

  if (( TOP_N > 0 )); then
    echo
    echo "## Largest Files"
    echo
    echo "| Path | ~Tokens | Share |"
    echo "|---|--:|--:|"
    for idx in $TOP_IDX; do
      echo "| \`$(md_escape "${F_REL[$idx]}")\` | $(fmt_num "${F_TOKENS[$idx]}") | $(percent "${F_TOKENS[$idx]}")% |"
    done
  fi

  echo
  echo "## Flags"
  echo
  if [[ -z "$OVER_IDX$EMPTY_IDX$DUPES" ]]; then
    echo "None: no oversized, empty, or duplicate files."
  fi
  for idx in $OVER_IDX; do
    echo "- **Over ~$(fmt_num "$WARN_TOKENS") tokens:** \`${F_REL[$idx]}\` (~$(fmt_num "${F_TOKENS[$idx]}"))"
  done
  for idx in $EMPTY_IDX; do
    echo "- **Empty:** \`${F_REL[$idx]}\`"
  done
  if [[ -n "$DUPES" ]]; then
    while IFS= read -r group; do
      IFS=$'\t' read -r -a parts <<< "$group"
      text="\`${parts[0]}\`"
      for (( i = 1; i < ${#parts[@]}; i++ )); do
        text+=" = \`${parts[$i]}\`"
      done
      echo "- **Identical content:** $text"
    done <<< "$DUPES"
  fi

  echo
  echo "## Summaries"
  for (( i = 0; i < ${#FILES[@]}; i++ )); do
    echo
    echo "### \`${F_REL[$i]}\`"
    echo
    echo "- **Title:** ${F_TITLE[$i]}"
    if [[ -n "${F_EXCERPT[$i]}" ]]; then
      echo "- **Summary:** ${F_EXCERPT[$i]}"
    fi
    echo "- **Shape:** ~$(plural "${F_TOKENS[$i]}" token) · $(plural "${F_LINES[$i]}" line) · $(plural "${F_HEADINGS[$i]}" heading)"
    if (( SHOW_OUTLINE )) && [[ -n "${F_OUTLINE[$i]}" ]]; then
      echo "- **Outline:**"
      while IFS=$'\t' read -r lvl text; do
        if [[ -n "$lvl" ]]; then
          printf '%*s- %s\n' $(( (lvl - F_OUTLINE_MIN[i] + 1) * 2 )) "" "$text"
        fi
      done <<< "${F_OUTLINE[$i]}"
    fi
  done
}

if [[ "$FORMAT" == "markdown" ]]; then
  render_fn=render_markdown
else
  render_fn=render_text
fi

if [[ -n "$OUTPUT" ]]; then
  "$render_fn" > "$OUTPUT"
  echo "$PROG: wrote $FORMAT report covering ${#FILES[@]} files to $OUTPUT" >&2
else
  "$render_fn"
fi
