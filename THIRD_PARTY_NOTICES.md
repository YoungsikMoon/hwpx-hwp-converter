# 제3자 오픈소스 고지

HWPX-HWP 변환기 자체 코드의 저작권은 문영식에게 있습니다. 아래 구성요소의 저작권은 각 원저작자에게 있으며 각 라이선스 조건에 따라 재배포됩니다.

| 구성요소 | 포함 버전 | 라이선스 | 원문 |
|---|---:|---|---|
| rhwp | @rhwp/core 0.8.2 | MIT | `licenses/MIT-rhwp.txt` |
| hwpConverter | commit 9af63ea | Apache-2.0 | `licenses/Apache-2.0-hwpConverter.txt` |
| PySide6 / Qt | 6.11.1 | LGPL-3.0-only OR GPL | `licenses/LGPL-3.0-Qt.txt`, `licenses/GPL-3.0.txt` |
| Eclipse Temurin OpenJDK | 21.0.12+8 | GPL-2.0 with Classpath Exception | `licenses/GPL-2.0-Classpath-Exception-OpenJDK.txt`, `licenses/OpenJDK-ADDITIONAL_LICENSE_INFO.txt` |
| Python | 3.11+ | PSF-2.0 | `licenses/PSF-Python.txt` |
| olefile | 0.47 | BSD-2-Clause | `licenses/BSD-2-Clause-olefile.txt` |
| defusedxml | 0.7.1 | PSFL | `licenses/PSFL-defusedxml.txt` |
| pywin32 | 312 | PSFL | `licenses/PSFL-pywin32.txt` |
| PyInstaller | 6.22.0 | GPL-2.0 with bootloader exception | `licenses/GPL-2.0-PyInstaller-Bootloader-Exception.txt` |

## Java 변환 라이브러리

hwpConverter와 함께 hwplib 1.1.10, hwpxlib 1.0.9, hwp2hwpx 1.0.0, Apache POI 5.2.5, Commons Codec, Commons Collections, Commons IO, Commons Math, Log4j API/Core, SparseBitSet 및 재배포 의존성을 포함합니다. 대부분 Apache-2.0이며 원본 JAR과 라이선스는 `vendor/hwp-converter`에 보존됩니다.

## Qt LGPL 안내

Qt/PySide6는 수정하지 않은 동적 라이브러리 형태로 포함됩니다. 사용자는 LGPL이 허용하는 범위에서 Qt 라이브러리를 수정하거나 그 수정 사항을 디버깅하기 위한 역공학을 할 수 있습니다. 프로그램 자체의 MIT 라이선스는 이를 제한하지 않습니다. LGPLv3와 함께 적용되는 GPLv3 전문도 배포물에 포함합니다.

## Java 런타임 고지

Eclipse Temurin OpenJDK의 전체 법적 고지와 구성요소별 제3자 라이선스는 `runtime/java/legal`에 포함되어 EXE와 함께 배포됩니다.

이 문서는 라이선스 준수를 위한 고지이며 법률 자문은 아닙니다.
