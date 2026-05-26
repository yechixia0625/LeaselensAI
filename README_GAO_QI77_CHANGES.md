# GAO-QI77 LeaseLensAI Extension README

> Dedicated change note for the GAO-QI77 contribution branch.

[中文](#中文说明) | [English](#english-notes)

---

## 中文说明

### 目的

本文档专门记录 GAO-QI77 在 LeaseLensAI 项目上的新增与修改内容。为尽量保留原项目结构和主 README 的叙事方式，本说明文件独立放置在仓库根目录，用于说明新增功能、影响范围、运行方式和验证重点。

### 改动摘要

本次贡献将 LeaseLensAI 从基础铺位评估原型扩展为更面向新加坡小商户和餐饮业态的租赁尽调系统。主要新增能力包括：

- 新加坡候选店址推荐：分析完成后固定返回 3 个可比较的 Singapore 候选位置。
- 60/40 混合评分模型：确定性规则最高 60 分，LLM 专业判断最高 40 分。
- F&B readiness 尽调：覆盖烹饪强度、供水、电力、燃气、地漏、隔油池、排烟、污水和批准用途。
- 租赁与装修假设增强：加入租期、服务费、装修预算、免租期、押金、运营成本和复原成本等变量。
- 前端工作台增强：增加评分拆解、风险标记、地点推荐和更完整的 What-if 模拟展示。
- 后端测试扩展：新增评分、API、LLM、Geo 和 pipeline 相关测试覆盖。
- Docker 与依赖整理：补充 `.dockerignore`、ESLint 配置、uv lock 和前端构建依赖调整。

### 功能层面

#### 1. 新加坡租赁评分与推荐

新增后端 scoring service，用于把财务、空间、监管和位置因素合并为结构化评分。最终报告中会包含：

- `summary.scoreBreakdown.fixedScore`
- `summary.scoreBreakdown.llmScore`
- `summary.scoreBreakdown.totalScore`
- `summary.scoreBreakdown.components`
- `summary.scoreBreakdown.riskFlags`
- `recommendedLocations`

其中 `recommendedLocations` 会返回 3 个新加坡候选位置，并附带区域、坐标、租金 benchmark、优劣势和公开来源链接字段。

#### 2. F&B Readiness 输入模型

前端 intake form 和后端 schema 新增餐饮租赁尽调字段：

- `cookingIntensity`
- `floorPosition`
- `layoutShape`
- `hasWaterSupply`
- `hasFloorTrap`
- `hasGreaseTrap`
- `electricalReadiness`
- `hasGas`
- `hasExhaust`
- `wastewaterReadiness`
- `approvedUseStatus`

这些字段会影响固定评分和风险标记，尤其适用于 cafe、bakery、restaurant、bar 等业态。

#### 3. 财务和运营假设扩展

新增或扩展的经营变量包括：

- 租期、服务费、装修预算、免租期和押金。
- 水电、人工、营销、保险、牌照、复原成本等月度或一次性费用。
- 预期客流、客单价、毛利率、座位数、使用面积比例等经营参数。

这些字段会被用于估算租金压力、月度运营成本、回本周期和 lease runway。

#### 4. 前端工作台增强

新增或改动的主要前端模块：

- `LocationRecommendations.tsx`
- `ScoreBreakdownPanel.tsx`
- `IntakeForm.tsx`
- `WorkspaceLayout.tsx`
- `AnalysisService.ts`
- `intakeTransfer.ts`

用户可以在分析工作台中看到更细的评分来源、风险原因和候选位置，而不是只看到单一结论。

#### 5. 后端测试增强

新增或扩展测试覆盖：

- `backend/tests/test_services/test_scoring.py`
- `backend/tests/test_api/test_analyze.py`
- `backend/tests/test_pipeline/test_orchestrator.py`
- `backend/tests/test_services/test_geo.py`
- `backend/tests/test_services/test_llm.py`

测试重点覆盖评分结构、F&B 表单字段、推荐位置、Google Places 兜底行为和 LLM JSON 解析。

### 主要文件范围

| Area | Files |
| --- | --- |
| Scoring | `backend/src/services/scoring.py`, `backend/src/models/schemas/summary.py` |
| Intake API | `backend/src/api/v1/analyze.py`, `backend/src/models/schemas/intake.py` |
| Recommendations | `backend/src/models/schemas/recommendation.py`, `frontend/src/components/workspace/LocationRecommendations.tsx` |
| Frontend form | `frontend/src/components/intake/IntakeForm.tsx`, `frontend/src/services/intakeTransfer.ts` |
| Workspace UI | `frontend/src/components/workspace/ScoreBreakdownPanel.tsx`, `frontend/src/components/workspace/WorkspaceLayout.tsx` |
| Simulation | `frontend/src/hooks/useWhatIf.ts`, `frontend/src/math/*` |
| Tests | `backend/tests/test_*` |
| Build support | `frontend/package.json`, `frontend/package-lock.json`, `backend/uv.lock`, `.dockerignore` files |

### 环境变量补充

新增或强调的变量：

```text
LEASENS_ONEMAP_ACCESS_TOKEN
LEASENS_GOOGLE_PLACES_API_KEY
LEASENS_GOOGLE_PLACES_SEARCH_RADIUS_METERS
```

`LEASENS_ONEMAP_ACCESS_TOKEN` 当前作为后续接入新加坡官方地理数据的预留变量。

### 运行方式

推荐继续使用项目原有的 portable compose 入口：

```bash
docker compose -f docker-compose.portable.yml up --build -d
```

访问：

```text
http://localhost:8080/
```

健康检查：

```bash
curl -i http://127.0.0.1:8080/api/v1/health
```

地址搜索检查建议使用新加坡地址：

```bash
curl -i -X POST http://127.0.0.1:8080/api/locations/autocomplete \
  -H 'Content-Type: application/json' \
  --data '{"input":"Tanjong Pagar Singapore","sessionToken":"session-token-1"}'
```

### 建议验证

推荐在合并前执行：

```bash
cd backend && pytest
```

```bash
cd frontend && npm run lint
```

如需完整部署验证，再执行：

```bash
docker compose -f docker-compose.portable.yml up --build -d
```

### 兼容性说明

- 本贡献尽量沿用原项目的目录结构、FastAPI 分层、Next.js 结构和 Docker Compose 入口。
- 通用 README 保持原项目说明方式，本文件作为 GAO-QI77 改动的专属说明。
- 新增模型字段向后兼容默认值，大部分 F&B readiness 字段在缺失时会使用 `unknown` 或默认数值。
- 推荐位置目前内置新加坡候选池和公开来源链接字段，后续可替换为更完整的数据源。

### 风险与限制

- 评分模型是辅助决策，不构成法律、财务、房地产或监管合规建议。
- 租金 benchmark 和候选位置为启发式估计，应结合真实经纪报价、业主条款和政府/物业规定复核。
- Google Places API Key 仅应在后端使用，不应暴露到前端。
- 生产环境仍需要更完整的认证、权限、审计和数据保留策略。

---

## English Notes

### Purpose

This document records the GAO-QI77 contribution to LeaseLensAI. It is intentionally separated from the main README so the original repository structure and primary project narrative can remain mostly unchanged while the new feature set is documented clearly.

### Change Summary

This contribution extends LeaseLensAI from a baseline retail-space evaluation prototype into a Singapore-oriented lease diligence system for small businesses and F&B operators.

Major additions include:

- Singapore candidate-location recommendations with 3 comparable suggested sites.
- A hybrid 60/40 score: deterministic rules up to 60 points and LLM judgement up to 40 points.
- F&B readiness diligence covering cooking intensity, water, power, gas, floor trap, grease trap, exhaust, wastewater and approved use.
- Expanded lease and fit-out assumptions such as lease term, service charge, fit-out budget, rent-free months, deposit, operating costs and reinstatement cost.
- Enhanced frontend workspace with score breakdown, risk flags, location recommendations and richer what-if simulation.
- Expanded backend tests for scoring, API contracts, LLM parsing, Geo behavior and pipeline orchestration.
- Docker and dependency maintenance, including `.dockerignore`, ESLint configuration, uv lock and frontend build adjustments.

### Functional Additions

#### 1. Singapore Lease Scoring and Recommendations

A backend scoring service now merges financial, spatial, regulatory and location factors into a structured report. The final report includes:

- `summary.scoreBreakdown.fixedScore`
- `summary.scoreBreakdown.llmScore`
- `summary.scoreBreakdown.totalScore`
- `summary.scoreBreakdown.components`
- `summary.scoreBreakdown.riskFlags`
- `recommendedLocations`

`recommendedLocations` returns 3 Singapore candidate sites with area, coordinates, rent benchmark, pros, cons and public-source link fields.

#### 2. F&B Readiness Model

The frontend intake form and backend schema now support F&B lease diligence fields:

- `cookingIntensity`
- `floorPosition`
- `layoutShape`
- `hasWaterSupply`
- `hasFloorTrap`
- `hasGreaseTrap`
- `electricalReadiness`
- `hasGas`
- `hasExhaust`
- `wastewaterReadiness`
- `approvedUseStatus`

These fields affect deterministic scoring and risk flags, especially for cafe, bakery, restaurant and bar use cases.

#### 3. Financial and Operating Assumptions

The contribution adds or expands:

- Lease term, service charge, fit-out budget, rent-free months and deposit.
- Utilities, staffing, marketing, insurance, license fees and reinstatement costs.
- Expected traffic, average spend, gross margin, seating capacity and usable area ratio.

These inputs support rent-pressure, monthly operating-cost, payback-period and lease-runway calculations.

#### 4. Frontend Workspace Enhancements

Key frontend additions and modifications include:

- `LocationRecommendations.tsx`
- `ScoreBreakdownPanel.tsx`
- `IntakeForm.tsx`
- `WorkspaceLayout.tsx`
- `AnalysisService.ts`
- `intakeTransfer.ts`

The workspace now exposes the reasoning behind the recommendation rather than only a single final verdict.

#### 5. Backend Test Coverage

New or extended tests include:

- `backend/tests/test_services/test_scoring.py`
- `backend/tests/test_api/test_analyze.py`
- `backend/tests/test_pipeline/test_orchestrator.py`
- `backend/tests/test_services/test_geo.py`
- `backend/tests/test_services/test_llm.py`

The tests focus on score structure, F&B form fields, candidate locations, Google Places fallback behavior and LLM JSON parsing.

### Main File Scope

| Area | Files |
| --- | --- |
| Scoring | `backend/src/services/scoring.py`, `backend/src/models/schemas/summary.py` |
| Intake API | `backend/src/api/v1/analyze.py`, `backend/src/models/schemas/intake.py` |
| Recommendations | `backend/src/models/schemas/recommendation.py`, `frontend/src/components/workspace/LocationRecommendations.tsx` |
| Frontend form | `frontend/src/components/intake/IntakeForm.tsx`, `frontend/src/services/intakeTransfer.ts` |
| Workspace UI | `frontend/src/components/workspace/ScoreBreakdownPanel.tsx`, `frontend/src/components/workspace/WorkspaceLayout.tsx` |
| Simulation | `frontend/src/hooks/useWhatIf.ts`, `frontend/src/math/*` |
| Tests | `backend/tests/test_*` |
| Build support | `frontend/package.json`, `frontend/package-lock.json`, `backend/uv.lock`, `.dockerignore` files |

### Additional Environment Variables

New or highlighted variables:

```text
LEASENS_ONEMAP_ACCESS_TOKEN
LEASENS_GOOGLE_PLACES_API_KEY
LEASENS_GOOGLE_PLACES_SEARCH_RADIUS_METERS
```

`LEASENS_ONEMAP_ACCESS_TOKEN` is reserved for future integration with official Singapore geospatial data.

### Running the Project

Use the existing portable compose entrypoint:

```bash
docker compose -f docker-compose.portable.yml up --build -d
```

Open:

```text
http://localhost:8080/
```

Health check:

```bash
curl -i http://127.0.0.1:8080/api/v1/health
```

Singapore address autocomplete check:

```bash
curl -i -X POST http://127.0.0.1:8080/api/locations/autocomplete \
  -H 'Content-Type: application/json' \
  --data '{"input":"Tanjong Pagar Singapore","sessionToken":"session-token-1"}'
```

### Recommended Validation

Before merging, run:

```bash
cd backend && pytest
```

```bash
cd frontend && npm run lint
```

For full deployment validation:

```bash
docker compose -f docker-compose.portable.yml up --build -d
```

### Compatibility Notes

- The contribution follows the existing FastAPI, Next.js and Docker Compose project organization.
- The main README remains in the original project style; this file documents the GAO-QI77-specific changes.
- New model fields use defaults such as `unknown` or numeric fallback values where possible.
- The current recommendation layer uses a Singapore candidate pool and public-source link fields; it can later be replaced with richer benchmark data.

### Risks and Limitations

- The scoring model is a decision-support tool, not legal, financial, real-estate or regulatory compliance advice.
- Rent benchmarks and candidate sites are heuristic estimates and should be verified against live broker quotes, landlord terms and government/property rules.
- Google Places API keys should remain server-side only.
- Production deployment still requires stronger authentication, authorization, auditing and data-retention policies.
