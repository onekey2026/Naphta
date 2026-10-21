# 나프타 시세 (오피넷)

한국석유공사 오피넷의 국제 석유제품 가격 중 싱가포르 나프타 일간 시세를 보여주는 정적 페이지입니다.
GitHub Actions가 2시간마다 오피넷을 조회해서, 값이 바뀌면 `data/naphtha.json`을 커밋하고 GitHub Pages에 다시 배포합니다.
방문자가 페이지를 열면 그 시점의 최신 JSON을 읽어 옵니다.

## 구성

| 파일 | 역할 |
|---|---|
| `index.html` | 차트 페이지 (Chart.js). `data/naphtha.json`을 읽음 |
| `data/naphtha.json` | 최근 3년 시세 (`date`, `usd_bbl`, `krw_l`) + 갱신 시각 |
| `scripts/fetch_naphtha.py` | 오피넷 조회 → JSON 저장 (값이 같으면 파일을 그대로 둠) |
| `.github/workflows/update-data.yml` | 2시간마다 실행 + push/수동 실행 시 배포 |

## 처음 설정 (한 번만)

1. GitHub에서 **Public** 저장소를 새로 만듭니다 (예: `naphtha`). 무료 계정의 Pages는 Public 저장소에서만 됩니다.
2. 이 폴더의 파일을 모두 올립니다. `.github` 폴더도 꼭 포함해야 합니다.
   - 웹에서 올릴 때: 저장소의 **Add file → Upload files**에 폴더째 끌어다 놓습니다.
   - git으로 올릴 때:
     ```
     git init -b main
     git add .
     git commit -m "Initial commit"
     git remote add origin https://github.com/<아이디>/naphtha.git
     git push -u origin main
     ```
3. 저장소 **Settings → Pages → Build and deployment → Source**를 **GitHub Actions**로 바꿉니다.
4. **Actions** 탭 → *Update naphtha data & deploy* → **Run workflow**로 한 번 실행합니다.
5. 끝나면 `https://<아이디>.github.io/naphtha/`에서 볼 수 있습니다.

## 참고

- 갱신 주기를 바꾸려면 `update-data.yml`의 `cron`을 고치면 됩니다 (UTC 기준).
- GitHub는 사용량이 많을 때 예약 실행을 몇 분에서 수십 분 늦게 돌리기도 합니다.
- 오피넷 응답 구조가 바뀌면 스크립트가 실패하고, Actions 탭에 빨간 표시가 뜹니다 (GitHub에서 메일 알림도 옵니다).
- 출처: 한국석유공사 오피넷 (https://www.opinet.co.kr). 공개 게시 전 오피넷 이용약관을 확인하세요.

## 로컬에서 미리 보기

```
python scripts/fetch_naphtha.py
python -m http.server 8000
```
브라우저에서 http://localhost:8000 을 엽니다. (`index.html`을 더블클릭해서 열면 JSON을 읽지 못합니다.)
