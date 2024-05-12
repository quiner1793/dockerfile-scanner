resource "github_repository" "terraform" {
  name             = "DevOpsCourse"
  description      = "DevOps course labs"
  visibility       = "public"
  has_issues       = true
  has_wiki         = true
  auto_init        = true
  license_template = "mit"
}

resource "github_branch_default" "main" {
  repository = github_repository.terraform.name
  branch     = "main"
}

resource "github_branch_protection" "default" {
  repository_id                   = github_repository.terraform.id
  pattern                         = github_branch_default.main.branch
  require_conversation_resolution = true
  enforce_admins                  = true

  required_pull_request_reviews {
    required_approving_review_count = 1
  }
}

resource "github_team" "teamA" {
  name        = "teamA"
  description = "team A"
}

resource "github_team" "teamB" {
  name        = "teamB"
  description = "team B"
}

resource "github_team_repository" "teamA_repo" {
  team_id    = github_team.teamA.id
  repository = github_repository.terraform.name
  permission = "pull"
}

resource "github_team_repository" "teamB_repo" {
  team_id    = github_team.teamB.id
  repository = github_repository.terraform.name
  permission = "admin"
}
