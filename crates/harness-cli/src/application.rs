use std::path::PathBuf;

use crate::domain::knowledge;
use crate::domain::{
    BacklogRecord, BoolFlag, CsvList, DecisionRecord, FrictionRecord, HarnessStats, InputType,
    IntakeRecord, RiskLane, StoryMatrixRecord, TraceRecord,
};
use crate::infrastructure::{HarnessRepository, KnowledgeWorkspace, SqliteHarnessRepository};

#[derive(Debug)]
pub struct HarnessContext {
    pub repo_root: PathBuf,
    pub db_path: PathBuf,
    pub schema_dir: PathBuf,
}

#[derive(Debug)]
pub struct IntakeInput {
    pub input_type: InputType,
    pub summary: String,
    pub risk_lane: RiskLane,
    pub risk_flags: CsvList,
    pub affected_docs: CsvList,
    pub story_id: Option<String>,
    pub notes: Option<String>,
}

#[derive(Debug)]
pub struct StoryAddInput {
    pub id: String,
    pub title: String,
    pub risk_lane: RiskLane,
    pub contract_doc: Option<String>,
    pub notes: Option<String>,
}

#[derive(Debug)]
pub struct StoryUpdateInput {
    pub id: String,
    pub status: Option<String>,
    pub evidence: Option<String>,
    pub unit: Option<BoolFlag>,
    pub integration: Option<BoolFlag>,
    pub e2e: Option<BoolFlag>,
    pub platform: Option<BoolFlag>,
}

#[derive(Debug)]
pub struct DecisionAddInput {
    pub id: String,
    pub title: String,
    pub status: String,
    pub doc_path: Option<String>,
    pub verify_command: Option<String>,
    pub predicted_impact: Option<String>,
    pub notes: Option<String>,
}

#[derive(Debug)]
pub struct BacklogAddInput {
    pub title: String,
    pub discovered_while: Option<String>,
    pub current_pain: Option<String>,
    pub suggestion: Option<String>,
    pub risk: Option<RiskLane>,
    pub predicted_impact: Option<String>,
    pub notes: Option<String>,
}

#[derive(Debug)]
pub struct BacklogCloseInput {
    pub id: i64,
    pub status: String,
    pub actual_outcome: Option<String>,
}

#[derive(Debug)]
pub struct TraceInput {
    pub task_summary: String,
    pub intake_id: Option<i64>,
    pub story_id: Option<String>,
    pub agent: Option<String>,
    pub outcome: Option<String>,
    pub duration_seconds: Option<i64>,
    pub token_estimate: Option<i64>,
    pub friction: Option<String>,
    pub notes: Option<String>,
    pub actions: CsvList,
    pub files_read: CsvList,
    pub files_changed: CsvList,
    pub decisions: CsvList,
    pub errors: CsvList,
}

pub struct HarnessService {
    repository: SqliteHarnessRepository,
}

impl HarnessService {
    pub fn new(context: HarnessContext) -> Self {
        Self {
            repository: SqliteHarnessRepository::new(
                context.repo_root,
                context.db_path,
                context.schema_dir,
            ),
        }
    }

    pub fn init(&self) -> crate::infrastructure::Result<InitResult> {
        self.repository.init()
    }

    pub fn migrate(&self) -> crate::infrastructure::Result<MigrateResult> {
        self.repository.migrate()
    }

    pub fn import_brownfield(&self) -> crate::infrastructure::Result<BrownfieldImportResult> {
        self.repository.import_brownfield()
    }

    pub fn record_intake(&self, input: IntakeInput) -> crate::infrastructure::Result<i64> {
        self.repository.record_intake(input)
    }

    pub fn add_story(&self, input: StoryAddInput) -> crate::infrastructure::Result<()> {
        self.repository.add_story(input)
    }

    pub fn update_story(&self, input: StoryUpdateInput) -> crate::infrastructure::Result<()> {
        self.repository.update_story(input)
    }

    pub fn add_decision(&self, input: DecisionAddInput) -> crate::infrastructure::Result<()> {
        self.repository.add_decision(input)
    }

    pub fn verify_decision(&self, id: &str) -> crate::infrastructure::Result<DecisionVerifyResult> {
        self.repository.verify_decision(id)
    }

    pub fn add_backlog(&self, input: BacklogAddInput) -> crate::infrastructure::Result<i64> {
        self.repository.add_backlog(input)
    }

    pub fn close_backlog(&self, input: BacklogCloseInput) -> crate::infrastructure::Result<()> {
        self.repository.close_backlog(input)
    }

    pub fn record_trace(&self, input: TraceInput) -> crate::infrastructure::Result<i64> {
        self.repository.record_trace(input)
    }

    pub fn query_matrix(&self) -> crate::infrastructure::Result<Vec<StoryMatrixRecord>> {
        self.repository.query_matrix()
    }

    pub fn query_backlog(&self) -> crate::infrastructure::Result<Vec<BacklogRecord>> {
        self.repository.query_backlog()
    }

    pub fn query_decisions(&self) -> crate::infrastructure::Result<Vec<DecisionRecord>> {
        self.repository.query_decisions()
    }

    pub fn query_intakes(&self) -> crate::infrastructure::Result<Vec<IntakeRecord>> {
        self.repository.query_intakes()
    }

    pub fn query_traces(&self) -> crate::infrastructure::Result<Vec<TraceRecord>> {
        self.repository.query_traces()
    }

    pub fn query_friction(&self) -> crate::infrastructure::Result<Vec<FrictionRecord>> {
        self.repository.query_friction()
    }

    pub fn query_stats(&self) -> crate::infrastructure::Result<HarnessStats> {
        self.repository.query_stats()
    }

    pub fn query_sql(&self, sql: &str) -> crate::infrastructure::Result<QueryTable> {
        self.repository.query_sql(sql)
    }
}

#[derive(Debug)]
pub struct KnowledgeScaffoldResult {
    pub path: PathBuf,
    pub created: bool,
}

/// Generate and verify the repository Knowledge Index. Pure rendering lives in
/// `domain::knowledge`; filesystem access lives in `KnowledgeWorkspace`.
pub struct KnowledgeService {
    workspace: KnowledgeWorkspace,
}

impl KnowledgeService {
    pub fn new(repo_root: PathBuf) -> Self {
        Self {
            workspace: KnowledgeWorkspace::new(repo_root),
        }
    }

    pub fn scaffold(&self) -> crate::infrastructure::Result<KnowledgeScaffoldResult> {
        self.workspace.ensure_index_dir()?;
        let inputs = self.workspace.gather()?;
        let existing = self.workspace.read_existing()?;
        let preserved = existing
            .as_deref()
            .map(knowledge::parse_preserved)
            .unwrap_or_default();
        let content = knowledge::render_index(&inputs, &preserved);
        let path = self.workspace.write_index(&content)?;
        Ok(KnowledgeScaffoldResult {
            path,
            created: existing.is_none(),
        })
    }

    pub fn check(&self) -> crate::infrastructure::Result<Vec<String>> {
        let inputs = self.workspace.gather()?;
        let existing = self.workspace.read_existing()?;
        Ok(knowledge::check_index(existing.as_deref(), &inputs))
    }
}

#[derive(Debug, PartialEq, Eq)]
pub enum InitResult {
    Created { db_path: PathBuf },
    Existing { db_path: PathBuf, version: i64 },
    MigratedExisting { db_path: PathBuf },
}

#[derive(Debug, PartialEq, Eq)]
pub struct MigrateResult {
    pub current_version: i64,
    pub applied: Vec<i64>,
}

#[derive(Debug, PartialEq, Eq)]
pub struct BrownfieldImportResult {
    pub stories: usize,
    pub decisions: usize,
    pub backlog_items: usize,
}

#[derive(Debug, PartialEq, Eq)]
pub struct DecisionVerifyResult {
    pub command: String,
    pub result: String,
}

#[derive(Debug, PartialEq, Eq)]
pub struct QueryTable {
    pub headers: Vec<String>,
    pub rows: Vec<Vec<String>>,
}

#[cfg(test)]
mod tests {
    use std::fs;

    use super::*;

    #[test]
    fn knowledge_scaffold_creates_preserves_and_passes_check() {
        let temp_dir = tempfile::tempdir().unwrap();
        let repo_root = temp_dir.path().join("demo");
        fs::create_dir_all(repo_root.join("src")).unwrap();
        fs::write(repo_root.join("Cargo.toml"), "[package]\nname=\"d\"\n").unwrap();

        let service = KnowledgeService::new(repo_root.clone());

        // First scaffold creates the index; check fails on TODO placeholders.
        let result = service.scaffold().unwrap();
        assert!(result.created);
        assert!(result.path.exists());
        assert!(!service.check().unwrap().is_empty());

        // Author Purpose, Key Concepts, and every structure description.
        // After the first scaffold, `docs/` exists and is also a listed entry.
        let index_path = repo_root.join("docs/KNOWLEDGE_INDEX.md");
        let authored = fs::read_to_string(&index_path)
            .unwrap()
            .replace(
                "TODO: Describe what this repository is for in 1-3 sentences (Purpose).",
                "A demo repo.",
            )
            .replace(
                "TODO: List the core concepts and terms an agent must know. See docs/GLOSSARY.md.",
                "Core terms.",
            )
            .replace("`Cargo.toml` — TODO: describe.", "`Cargo.toml` — Manifest.")
            .replace("`docs/` — TODO: describe.", "`docs/` — Docs.")
            .replace("`src/` — TODO: describe.", "`src/` — Source.");
        fs::write(&index_path, authored).unwrap();
        assert!(service.check().unwrap().is_empty());

        // Re-scaffold is idempotent and preserves authored content.
        let result = service.scaffold().unwrap();
        assert!(!result.created);
        let refreshed = fs::read_to_string(&index_path).unwrap();
        assert!(refreshed.contains("A demo repo."));
        assert!(refreshed.contains("`Cargo.toml` — Manifest."));
        assert!(service.check().unwrap().is_empty());
    }
}
