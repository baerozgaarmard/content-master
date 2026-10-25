# Content Master MCP tools

Content Master currently exposes exactly five MCP tools. All tools operate as the workspace selected during OAuth unless explicitly described as a global search.

## `filters`

Lists automation filters configured for the selected workspace. This tool is read-only.

Optional input:

- `status`: `all`, `active`, or `inactive`.

It returns filter names, active status, channel scope, performance thresholds, daily analysis limits, and scheduling information. Filters must be created or changed in **Setup → Automations** in Content Master.

Example request:

```text
Use Content Master to list my active automation filters. Return only the filter names.
```

## `videos-watchlist`

Lists and ranks videos associated with channels tracked in the selected workspace.

Optional inputs include:

- Keyword
- Platform: YouTube, TikTok, Instagram, or all
- Minimum and maximum views
- Minimum and maximum outlier score
- Minimum and maximum engagement rate
- Number of recent posting days
- Exclude boosted videos
- Analysis status
- Sorting, limit, and pagination offset

The maximum result limit is 50. Results include creator information, metrics, a direct watch link, analysis status, and the next available analysis action.

## `video-global`

Searches video titles and descriptions across the global Content Master database using keyword relevance. The user must provide a topic or keyword `query`; the older `keyword` input remains available as an alias.

Optional inputs include:

- Additional exact search terms
- Platform
- View, outlier-score, and engagement ranges
- Number of recent posting days
- Sorting and result limit

The maximum result limit is 50. This search is global rather than restricted to the selected workspace's watchlist.

## `analyze`

Starts or reuses an analysis for exactly one video.

Required input—provide exactly one:

- `url`: a supported YouTube, TikTok, or Instagram video URL.
- `video_id`: an existing Content Master video UUID.

This tool requires the `content-master:analyze` permission. If a URL is supplied, Content Master loads the video and makes its channel available through the selected workspace's default watchlist. If the workspace already has a completed analysis, the result is reused. Otherwise, a successful new workspace unlock costs one credit.

If the response says the analysis is processing, use the returned `video_id` with `analysis-result`.

## `analysis-result`

Checks an analysis started or reused by `analyze`.

Required input:

- `video_id`: the UUID returned by `analyze`.

Possible states include not started, processing, failed, and completed. A completed response may contain source metrics, transcript, idea analysis, hook analysis, storytelling analysis, and visual-layout analysis. Empty sections are omitted.

## Permissions and charging summary

| Tool | Permission | Can start a credit charge? |
|---|---|---:|
| `filters` | `content-master:read` | No |
| `videos-watchlist` | `content-master:read` | No |
| `video-global` | `content-master:read` | No |
| `analyze` | `content-master:analyze` | Yes, for a successful new workspace unlock |
| `analysis-result` | `content-master:read` | No |

Content Master checks workspace membership for authenticated requests. Video-specific workspace tools also verify that the selected workspace can access the requested video.
