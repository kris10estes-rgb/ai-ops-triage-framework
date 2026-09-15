# Archive

Superseded documents kept for reference. **Don't build from anything in this folder.**

`workspace_sweep.sh` skips this folder by default, so archived files don't appear in `CONTEXT_INDEX.md` or count toward workspace token totals. Run the sweep with `-a` to include them.

Files keep their original folder structure (`archive/<original folder>/<file>`).

| File | Superseded By | Archived | Reason |
|---|---|---|---|
| `01_product_strategy/PRD_customer_support_triage.md` (PRD-2026-001) | `01_product_strategy/PRD_support_triage_bot.md` (PRD-2026-002) | 2026-09-15 | Replaced by a PRD with a tiered model routing matrix and corporate (B2B) email handling |
| `02_tech_architecture/ARCH_customer_support_triage.md` | `02_tech_architecture/ARCH_support_triage_bot.md` | 2026-09-15 | Written for PRD-2026-001; replaced by an architecture covering the new routing matrix and API error handling |

**To archive a document:**
1. Set its Status to Superseded and name its replacement.
2. Move it here under the same folder path.
3. Update links in the folder README and in the replacing document.
4. Add a row to this table.
5. Regenerate the index: `./03_operations_sprints/workspace_sweep.sh -m -o CONTEXT_INDEX.md`
