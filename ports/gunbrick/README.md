# Gunbrick Reloaded — NextOS / PortMaster

**Language / Idioma:** [English](#english) · [Português](#português)

Independent AArch64 Linux compatibility port for the Android release of
**Gunbrick Reloaded** (Unity 2022.3 IL2CPP). The release is BYO-data: it
contains the open-source loader and integration only, never the APK, Android
libraries, assets, videos or saves.

## English

### Status

Version 0.2.0 was validated end to end with the supported v10 ARM64 payload on
three NextOS device families:

- Amlogic Mali-450 using the native `mali`/framebuffer video path;
- X5M using KMSDRM and a Mali-G310;
- Ark using KMSDRM and a Mali-G31.

On every target, NXExtract displayed its clean setup UI, transactionally
installed the owner payload, and the game reached rendered gameplay with
audible SDL audio and a working controller. The tested APK was user supplied
and is not redistributed or claimed as an original store artifact; the exact
payload files are independently pinned by size, SHA-256 and asset-tree
fingerprint.

### Architecture

`Gunbrick.sh` is a generated, self-contained nxbootstrap 0.6 launcher. It
locates PortMaster, runs NXExtract before touching guest data, verifies the
manifest-owned runtime files, isolates game library paths from host setup,
publishes the nxcompat contract and returns cleanly to the frontend.

The adapter preserves the Android lifecycle:

1. map `libmain.so`, `libunity.so` and `libil2cpp.so` in dependency order;
2. relocate locally, resolve imports strictly and finalize guest mappings;
3. execute initializer arrays once and require JNI 1.6 from `JNI_OnLoad`;
4. let Unity `NativeLoader` establish readiness, then call `initJni`;
5. deliver surface creation/change, focus and resume before rendering;
6. deliver focus loss and pause before input/audio shutdown.

The framework is capability driven. SDL GLES2 is preferred; raw EGL is used
only after a real SDL window failure. nxcompat publishes measured EGL, GLES,
drawable, audio and controller receipts before `READY`. There are no device-IP
branches, forced firmware names, global texture-wrap changes, alpha hacks or
fixed-RVA gameplay patches.

### Controls

The loader forwards the standard Android controller buttons, both sticks,
triggers and D-pad through Unity's native input API. `SELECT + START` requests
a graceful exit. The optional directional-swipe compatibility quirk remains
narrow and is enabled only by the port contract when required; it does not
replace the native lifecycle or install a debug cursor.

### Owner data

Place a compatible Gunbrick Reloaded v10 ARM64 APK in `gunbrick/gamedata/` and
launch the port. NXExtract 1.2.6 checks package identity
`com.nitrome.Gunbrick`, selects `arm64-v8a`, verifies exactly 13 asset files
and all three Android ELFs, then publishes `assets/` and `lib/` atomically. A
wrong, partial or different-version payload is rejected without replacing a
working installation. The source APK is preserved.

### Build and verification

```bash
./build_universal.sh
./tests/run-host.sh
./package/build-package.sh
```

The public binary is built in a pinned offline Debian Buster environment and
must stay at or below GLIBC 2.30 (currently GLIBC 2.27). Gates reject RPATH,
RUNPATH, RWE load segments, unexpected dependencies, missing framework
symbols, owner data and private machine paths. NXRelease creates a
deterministic allowlisted ZIP, audits every included Linux ELF and reopens the
archive for verification.

### Source map and licenses

- `src/main.c`: Android/Unity lifecycle and graceful termination;
- `src/nx_elf.c`: strict guest ELF loading;
- `src/jni.c`, `src/android.c`, `src/bionic.c`: Android ABI bridge;
- `src/egl_sdl.c`, `src/egl.c`: SDL GLES2 and raw-EGL fallback;
- `src/input.c`, `src/audio.c`: controller and SDL audio;
- `src/framework_bridge.c`: nxcompat runtime receipts;
- `extractor.json`, `nxextract/`: transactional BYO-data installation.

Project code is GPL-3.0-only (`LICENSE`). NXExtract is MIT
(`licenses/NXExtract-MIT.txt`). Gunbrick Reloaded and its data remain property
of Nitrome or their respective rightsholders and are not distributed. See
`NOTICE.md`.

## Português

### Estado

Esta é uma camada de compatibilidade Linux AArch64 independente para a versão
Android de **Gunbrick Reloaded**. A versão 0.2.0 foi validada do começo ao fim
com o payload ARM64 v10 compatível em três famílias NextOS: Mali-450 por
`mali`/framebuffer, X5M por KMSDRM/Mali-G310 e Ark por KMSDRM/Mali-G31.

Nos três casos a interface limpa do NXExtract apareceu, os dados foram
instalados transacionalmente e o jogo chegou ao gameplay renderizado com áudio
audível e controle reconhecido. O APK usado no teste foi fornecido pelo usuário
e não é redistribuído nem apresentado como artefato original da loja; os
arquivos úteis são validados por tamanho, SHA-256 e fingerprint da árvore.

### Arquitetura e framework

`Gunbrick.sh` é um launcher enxuto de uso e autossuficiente, gerado pelo
nxbootstrap 0.6. Ele prepara PortMaster e o extrator, valida o payload exigido,
isola as bibliotecas do jogo e devolve a tela ao frontend na saída.

O adapter conserva a sequência Android real: bibliotecas, relocação e imports,
initializers, `JNI_OnLoad`, `NativeLoader`, `initJni`, surface, foco, resume e
render. Na saída executa perda de foco e pause. SDL GLES2 é a primeira opção e
EGL bruto só entra depois de falha real. O nxcompat exige evidência medida de
vídeo, áudio e input; não escolhe solução por IP ou nome de aparelho.

### Controles e dados

Botões, D-pad, analógicos e gatilhos seguem a API Android nativa do Unity.
`SELECT + START` pede saída limpa. O ZIP é BYO e não contém APK, bibliotecas
Android, assets, vídeos nem saves.

Coloque um APK ARM64 compatível do Gunbrick Reloaded v10 em
`gunbrick/gamedata/` e abra o port. O NXExtract 1.2.6 verifica o pacote
`com.nitrome.Gunbrick`, exatamente 13 arquivos de assets e as três bibliotecas,
depois publica `assets/` e `lib/` de forma atômica. Payload errado ou incompleto
é recusado sem destruir uma instalação válida; o APK de origem permanece no
local.

### Build, fontes e licenças

Use os três comandos da seção inglesa. O ELF público exige no máximo GLIBC
2.30 (atualmente 2.27), não aceita RPATH/RWX e o ZIP determinístico é reaberto
e auditado. O mapa de fontes também está acima.

O código do projeto é GPL-3.0-only e o NXExtract é MIT. Gunbrick Reloaded e
todos os dados do jogo continuam proprietários da Nitrome ou de seus titulares
e não fazem parte desta distribuição. Consulte `NOTICE.md`.
