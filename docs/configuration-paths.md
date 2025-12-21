# Configuration File Paths

This document describes all configuration file paths used by the Charcoal CLI and their purposes.

## Configuration Files

### User Configuration
- **Path**: `~/.graphite_user_config`
- **Format**: JSON
- **Purpose**: Stores user-specific preferences that apply across all repositories
- **Environment Override**: `GRAPHITE_USER_CONFIG_PATH` - Set this environment variable to use a custom path for user configuration
- **File Permissions**: 0o600 (owner read/write only)

**Fields**:
- `branchPrefix`: Optional prefix for branch names
- `branchDate`: Whether to include date in branch names
- `branchReplacement`: Character to use for replacing spaces in branch names ('_', '-', or '')
- `tips`: Whether to show helpful tips
- `editor`: Preferred editor (falls back to git config, then environment variables)
- `pager`: Preferred pager for output (falls back to git config, then environment variables)
- `restackCommitterDateIsAuthorDate`: Whether to preserve author date when restacking
- `submitIncludeCommitMessages`: Whether to include commit messages in PR submissions
- `connectCliToLocalServer`: Connect to local development server instead of production
- `gtiConfigs`: Array of GTI configuration key-value pairs
- `alternativeProfiles`: Array of alternative profile configurations with hostPrefix

### Repository Configuration
- **Path**: `.git/.graphite_repo_config`
- **Format**: JSON
- **Purpose**: Stores repository-specific settings
- **File Permissions**: 0o600 (owner read/write only)

**Fields**:
- `host`: Repository host (e.g., 'github.com')
- `owner`: Repository owner/organization
- `name`: Repository name
- `trunk`: Name of the trunk/main branch
- `remote`: Name of the git remote (defaults to 'origin')
- `lastFetchedPRInfoMs`: Timestamp of last PR info fetch
- `isGithubIntegrationEnabled`: Whether GitHub integration is enabled (defaults to true)

## TypeScript/Python Compatibility

The Python implementation uses **exactly the same file paths and formats** as the TypeScript implementation to ensure round-trip compatibility. This means:

1. Configuration files written by the Python CLI can be read by the TypeScript CLI
2. Configuration files written by the TypeScript CLI can be read by the Python CLI
3. Both implementations use the same JSON structure with camelCase field names
4. Both implementations set the same file permissions (0o600)
5. Both implementations use 2-space indentation for pretty-printed JSON

## File Path Resolution

### User Configuration Path Resolution
1. Check `GRAPHITE_USER_CONFIG_PATH` environment variable
2. Fall back to `~/.graphite_user_config`

### Repository Configuration Path Resolution
1. Look for `.git/.graphite_repo_config` in the current repository
2. Repository root is determined using `git rev-parse --show-toplevel`

## Notes

- Configuration files are created automatically on first use with default values
- Missing or malformed configuration files will be recreated with defaults (depending on settings)
- All file paths are absolute after resolution
- The `~` character is expanded to the user's home directory
- Configuration files are validated using Pydantic schemas before loading
