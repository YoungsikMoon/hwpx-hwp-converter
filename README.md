# HWPX-HWP 변환기

한컴오피스 2010 이하에서 열 수 없는 `.hwpx` 문서를 실제 HWP 5.x 바이너리 문서로 변환하는 Windows 프로그램입니다. 파일 확장자만 바꾸는 프로그램이 아닙니다.

- 버전: 1.0.0
- 개발자: 문영식
- 저작권: Copyright © 2026 문영식
- 프로그램 자체 라이선스: MIT

[Windows 실행 파일 다운로드](https://github.com/YoungsikMoon/hwpx-hwp-converter/releases/latest)

## 해결하려는 문제와 구현 범위

문서를 받은 사람이 구형 한컴오피스를 사용한다는 이유로 파일을 열지 못하는 상황을 줄이기 위한 개인 프로젝트입니다. 변환 엔진을 처음부터 작성하는 대신 기존 오픈소스 엔진을 Windows 앱으로 연결하고, 파일 선택부터 결과 확인까지 한 흐름으로 구성했습니다.

Python·PySide6 기반 UI에 입력 검증, 변환 실행, 결과 검증, 원본과 결과 비교를 연결했습니다. 변환 성공 표시만으로 문서 품질을 보장하기 어려워 경고와 좌우 미리보기를 함께 제공합니다.

| 확인할 내용 | 코드 |
| --- | --- |
| 변환 작업 흐름과 엔진 연결 | [orchestrator.py](src/hwpx_hwp_app/orchestrator.py), [engines.py](src/hwpx_hwp_app/engines.py) |
| 입력·결과 문서 검증 | [input_validator.py](src/hwpx_hwp_app/input_validator.py), [hwp_validator.py](src/hwpx_hwp_app/hwp_validator.py) |
| 문서 비교와 미리보기 | [comparator.py](src/hwpx_hwp_app/comparator.py), [preview_window.py](src/hwpx_hwp_app/preview_window.py) |
| 회귀 검증 | [tests](tests) |

## 사용법

1. `HWPX-HWP-변환기-1.0.0.exe`를 실행합니다.
2. `HWPX 파일 추가`를 누르거나 파일을 창에 끌어놓습니다.
3. 저장 폴더를 선택하고 `HWP로 변환`을 누릅니다.
4. 변환된 행의 맨 앞 미리보기 버튼을 누르면 원본 HWPX와 결과 HWP를 좌우로 비교할 수 있습니다.

좌우 미리보기는 페이지 이동, 확대·축소, 가로·세로 스크롤이 각각 독립적으로 작동합니다. 변환과 미리보기 모두 한컴오피스나 인터넷 연결 없이 내장 엔진으로 처리됩니다.

## 주의사항

HWPX와 구형 HWP가 지원하는 기능은 완전히 같지 않습니다. 텍스트, 표, 이미지, 글꼴, 문단, 페이지 서식은 최대한 보존하지만 최신 개체나 차트, OLE, 스크립트 등은 달라질 수 있습니다. 프로그램이 경고를 표시한 문서는 결과를 육안으로 확인하십시오.

원본과 이미 존재하는 HWP 파일은 덮어쓰지 않습니다. 같은 결과 이름이 있으면 번호를 붙여 새 파일을 생성합니다.

## 오픈소스

프로그램은 rhwp, hwpConverter, PySide6/Qt, Eclipse Temurin OpenJDK 및 여러 오픈소스 라이브러리를 포함합니다. 각 구성요소의 저작권은 원저작자에게 있으며 프로그램의 `도움말 → 오픈소스 라이선스`, [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), [licenses](licenses)에서 상세 내용을 확인할 수 있습니다.

## 자체검사

```powershell
HWPX-HWP-변환기-1.0.0.exe --self-test
```

## 지원 환경

- Windows 10/11 64비트
- 결과 호환 목표: HWP 5.x를 지원하는 한컴오피스 2010 이하
