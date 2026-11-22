# ytm-network-grace

> 비공식 개인용 빌드입니다. MorpheApp, seo-rii와 무관하며 공식 제품이 아닙니다.

[seo-rii/morphe-wireguard-patches](https://github.com/seo-rii/morphe-wireguard-patches)(공식 Morphe에 앱 전용 WireGuard를 넣은 비공식 패치)의 새 릴리스가 나올 때마다, 거기에 **크로스페이드 네트워크 유예** 패치를 얹어 `.mpp` 번들을 빌드하고 이 저장소의 릴리스로 올리는 개인용 자동화입니다.

크로스페이드 패치(`patches/crossfade-network-grace.patch`)는 WireGuard가 켜져 있을 때 YouTube Music 크로스페이드가 다음 곡 버퍼링을 최대 5초까지 기다려 주도록 합니다.

## 동작

`.github/workflows/build.yml`이 매일 1회(UTC 03:23) 또는 수동으로 실행됩니다.

1. seo-rii의 최신 릴리스 태그를 조회합니다. 이 저장소에 `<태그>-crossfade` 릴리스(예: `v2.2.0-crossfade`)가 이미 있으면 종료합니다.
2. seo-rii를 그 태그로 checkout하고 `scripts/find-base-commit.py`로 공식 기준 커밋을 찾습니다. 문서(`README.md`, `docs/wireguard-source-build.md`)와 패치 헤더(`README-WIREGUARD.md`)의 커밋 후보 중, 공식 저장소에서 받을 수 있고 패치의 모든 원본 blob(`index` 줄)과 일치하는 것이 **정확히 하나**일 때만 채택합니다. 못 찾으면 실패합니다.
3. 공식 `MorpheApp/morphe-patches`를 그 커밋으로 checkout하고 `wireguard-prototype.patch` → `patches/crossfade-network-grace.patch`(`git apply --3way`) 순으로 적용합니다.
4. seo-rii 빌드 스크립트가 고정한 Go·NDK 버전과 JDK 21을 설치하고, 문서의 공개 소스 경로(GitHub Packages 토큰 불필요)로 네이티브 `.so`와 `.mpp`를 빌드합니다.
5. `ytm-network-grace-<버전>.mpp`와 `.sha256`을 릴리스로 올립니다. 릴리스 노트에 seo-rii 태그/커밋, 공식 기준 커밋, 크로스페이드 패치 적용 사실이 적힙니다.

비밀값은 쓰지 않습니다. 기본 `GITHUB_TOKEN`만 사용하고 외부 공개 저장소는 인증 없이 읽습니다.

## 수동 실행

```sh
gh workflow run build.yml                       # 새 태그가 있을 때만 빌드
gh workflow run build.yml -f force=true         # 같은 태그라도 다시 빌드(기존 릴리스 교체)
gh workflow run build.yml -f seo_tag=v2.2.0     # 특정 seo-rii 태그를 빌드
gh run watch
```

## 패치가 충돌할 때

크로스페이드 패치가 적용되지 않으면 워크플로가 실패하고 이 저장소에 이슈가 자동 생성됩니다(업스트림 코드가 바뀐 것이므로 사람이 고쳐야 합니다).

1. 공식 기준 커밋(이슈에 적힘)을 받아 seo-rii 패치를 적용합니다.
   ```sh
   git clone https://github.com/MorpheApp/morphe-patches && cd morphe-patches
   git checkout <기준 커밋>
   git apply <seo-rii>/wireguard-prototype.patch
   git add -A
   ```
2. 크로스페이드 변경(`CrossfadePatch.java`, `Settings.java`, `CrossfadePatch.kt`, music 문자열 영/한)을 새 코드에 맞게 직접 다시 적용합니다. 1번에서 `git add -A` 했으므로 `git diff`(스테이지 안 된 변경)가 크로스페이드 변경만 담습니다: `git diff > crossfade-network-grace.patch`.
3. `patches/crossfade-network-grace.patch`를 교체하고 push한 뒤 `gh workflow run build.yml -f force=true`로 다시 실행합니다.

## Morphe Manager에서 쓰기

이 저장소는 **비공개**라서 Morphe Manager의 Remote 패치 소스로 등록할 수 없습니다. 릴리스 페이지(또는 `gh release download <태그>-crossfade`)에서 `.mpp`를 받아 Manager에 **로컬 번들로 직접 추가**하세요. `.sha256`으로 무결성을 확인할 수 있습니다.

빌드는 서명되지 않은 번들이며, GitHub Actions(Linux)에서 빌드하므로 seo-rii의 공식 릴리스와 바이트 단위로 같지 않습니다.

## 라이선스

업스트림과 같은 **GPLv3**(추가 GPL 섹션 7 조건 포함)를 따릅니다. 이 저장소의 스크립트·패치는 [MorpheApp/morphe-patches](https://github.com/MorpheApp/morphe-patches)와 seo-rii의 수정본에서 파생된 것으로, 해당 라이선스와 고지를 그대로 유지합니다. 비공식 빌드이며 MorpheApp, Proton 또는 seo-rii의 공식 제품이 아닙니다.
