# Bomb Chicken v44 — universal compatibility port (AArch64 / Unity IL2CPP)

**Language / Idioma:** [English](#english) · [Português](#português)

Bomb Chicken is proprietary software. This repository and the public release
contain the free compatibility loader and integration only. A lawful Android
copy of the game is required; no game executable, library, artwork, audio or
asset is redistributed.

## English

### Status and support boundary

The original 1.0 port was physically proven playable on a NextOS AArch64
Mali-450/GLES2 handheld: image, audio, controller, pause/resume, level
progression and orderly exit all worked. Version 1.1.1 migrates its public
launcher, contract, data extraction and low-glibc build to the universal
framework while deliberately preserving the proven Unity adapter and native
lifecycle.

The 1.1.1 loader builds reproducibly with a maximum requirement of
`GLIBC_2.27`, below the public `GLIBC_2.30` ceiling. Its host-only contract and
package gates pass without starting SDL, EGL, GLES, a game process or a test
device. The new package still needs physical validation of the exact release
ZIP before it can be promoted as multi-firmware. A successful host gate is not
a claim that every AArch64 firmware or GPU is supported.

### Architecture

The generated framework 0.5.1 launcher is the package's only launcher. It
validates the static deployment receipt, resolves capabilities supplied by the
host and exports only the quirks declared in `nxport.json`. It then starts
`bombchicken-nextos` directly; the package contains no nested `run.sh`,
firmware-name branch or process-table scan.

When that new launcher reaches its declared prepare phase, version 1.1.1 checks
the four known 1.0 overlay residues by exact SHA-256 and moves matching bytes out
of the active port directory into a non-executable
`.nxlegacy-bombchicken-v1/` quarantine. On FAT/exFAT storage that cannot retain
the non-executable mode, that byte-exact quarantined residue is removed instead.
Unknown bytes, symlinks and other file types are preserved and stop the launch
for manual review. The migration names only `run.sh`, `es_map.sh`, `es2sdl.awk`
and the old `bombchicken` loader; it never scans processes or another ROM root
and never touches `assets/`, `lib/`, `home/`, `gamedata/` or saves.

This makes a clean install and a PortMaster update on the same active scripts
root safe. It cannot remove an old visible launcher left on an inactive card or
the other muOS root. If you changed the PortMaster storage root between versions,
uninstall/remove that old menu entry explicitly or perform a clean installation
before using the new entry.

The compiled adapter remains game-specific. It maps the owner's original
AArch64 `libmain.so`, `libunity.so` and `libil2cpp.so`, supplies the Android/JNI,
EGL/GLES, audio and input surface they actually use, and drives the APK's
observed Android lifecycle in its original order:

1. map and relocate `libmain` → `libunity` → `libil2cpp`;
2. run `libmain` constructors, then its `JNI_OnLoad`;
3. call the registered `NativeLoader.load`, which runs the real `libunity` and
   `libil2cpp` constructors/`JNI_OnLoad` in that order;
4. call `initJni`, surface-created, surface-changed, focus and resume;
5. run the real `nativeRender` loop;
6. on exit, send focus-lost and pause before closing input and audio.

No entry point, constructor or lifecycle phase is skipped. This migration does
not pretend that the proven adapter has already been replaced by every shared
runtime component; the universal framework owns the pre-runtime contract and
launcher boundary, while the Unity compatibility code remains in `src/`.

### Game-specific quirks

All compatibility corrections default off and are enabled only by exact
newline-delimited tokens from the generated contract:

| Contract token | Evidence-backed purpose |
|---|---|
| `game.bombchicken.menu-cursor-v44` | polished right-stick pointer for the v44 touch-only menu; R3 clicks |
| `game.bombchicken.native-pause-v44` | invokes v44 `LevelStart.PausePressed()` and the native resume path |
| `game.bombchicken.nonnull-play-games-v44` | supplies a live JNI object where v44 Play Games code dereferences an optional service |
| `game.bombchicken.present-alpha-one` | preserves visible RGB on compositors that blend the default framebuffer by alpha |
| `game.bombchicken.progress-parser-v44` | safely handles malformed/trailing `Progress` records at level completion |
| `game.bombchicken.stencil8-v44` | supplies the stencil format requested by the proven v44 render path |

Graphics selection is capability-first. The adapter tries an SDL-owned GLES2
context and uses the raw EGL path only when that probe fails or an explicit
diagnostic override requests it. It does not select a path by firmware, device
or GPU name.

### Controls

| Control | Action |
|---|---|
| D-pad / left stick | move |
| A | confirm in menus; place a bomb in a level |
| B | place a bomb |
| Start | start from the title; pause/resume in a level |
| Right stick | move the pointer in touch-only menus |
| R3 | click the menu pointer |
| Select + Start | orderly lifecycle exit |

Controller mappings come from the host framework/SDL. The port does not ship a
device GUID or controller-name override. A capability-based raw-joystick and
evdev fallback remains for handhelds whose real controls are not exposed by
SDL's controller database.

### Owner-provided data with NXExtract 1.2.6

Only **Bomb Chicken Android v44 / build 45**, package
`com.nitrome.bombchicken`, ABI `arm64-v8a`, matches the exact extraction
contract. Place your lawful APK in the installed port's `gamedata/` directory
and start the visible launcher. NXExtract 1.2.6 validates the package, all three
native-library hashes and the complete Unity asset-tree fingerprint before it
atomically installs `assets/` and `lib/`.

Do not unpack files manually and do not add them to the source or public ZIP.
The accepted payload evidence and unmodified NXExtract hashes are documented
in `nxextract-version.txt`; the executable recipe is `extractor.json`.

### Build, test and release

The public loader is built inside a pinned, offline Debian Buster image. The
target sysroot is mounted read-only for SDL2/EGL/GLES headers only; no
high-glibc target library is linked into the output.

```sh
cd ports/bombchicken
./build.sh
./tests/run-host.sh
```

The gate performs the exact NXExtract recipe check, contract/privacy checks,
two clean builds and a byte-for-byte reproducibility comparison. It audits
every project-built ELF for architecture, interpreter, `DT_NEEDED`,
RPATH/RUNPATH and symbol-version requirements. It never launches the game or
touches a device. Public packaging is produced only by the deterministic
NXRelease recipe after framework-generated artifacts are pinned.

Useful opt-in diagnostics include `BC_VERBOSE=1`, `BC_LOGCAT=1`,
`BC_JNILOG=1`, `BC_GLLOG=1`, `BC_AUDIO_TRACE=1`, `BC_FPS=1` and the bounded
frame limit `BC_FRAMES=N`. They are not enabled by the public contract. The
deterministic public bundle is audited and re-opened by NXRelease 0.2.5.

### Source map

- `src/main.c` — contract-to-quirk bridge and exact Unity lifecycle.
- `src/nx_elf.c` — AArch64 Android ELF mapping, relocation and init arrays.
- `src/jni.c` / `src/android.c` — JNI and Android service compatibility.
- `src/egl.c` / `src/egl_sdl.c` — EGL/GLES2 surface, presentation and ETC2 hooks.
- `src/input.c` — SDL/Android input bridge and exact v44 gameplay corrections.
- `src/audio.c` — Unity FMOD/OpenSL-to-SDL audio path.
- `nxport.json` — universal capability and quirk contract.
- `extractor.json` — exact BYO-data recipe.
- `tests/` — process-free host contract, extraction and ELF gates.

### License and acknowledgements

The compatibility code and integration are GPL-3.0-only; see `LICENSE` and
`NOTICE.md`. NXExtract 1.2.6 is MIT-licensed; see
`licenses/NXExtract-MIT.txt`. Upstream interoperability acknowledgements are
recorded in `NOTICE.md`. Bomb Chicken and all owner data remain the property of
their respective rightsholders. This independent project is not affiliated
with or endorsed by Nitrome, Unity or Google.

---

## Português

### Estado e limite de suporte

O port 1.0 original foi comprovado fisicamente como jogável em um portátil
NextOS AArch64 com Mali-450/GLES2: imagem, áudio, controle, pausa/retomada,
progresso de fase e saída ordenada funcionaram. A versão 1.1.1 migra launcher
público, contrato, extração de dados e build de glibc baixa para o framework
universal, preservando de propósito o adaptador Unity e o ciclo de vida já
comprovados.

O loader 1.1.1 compila de forma reproduzível exigindo no máximo `GLIBC_2.27`,
abaixo do teto público `GLIBC_2.30`. Os gates de contrato e pacote rodam apenas
no host, sem iniciar SDL, EGL, GLES, jogo ou aparelho. O ZIP exato da nova
versão ainda precisa de validação física antes de receber promoção
multi-firmware. Passar no host não significa que todo firmware AArch64 ou toda
GPU já tenha suporte comprovado.

### Arquitetura

O launcher gerado pelo framework 0.5.1 é o único launcher do pacote. Ele valida
o receipt estático de instalação, resolve as capacidades entregues pelo host e
exporta somente os quirks declarados em `nxport.json`. Depois chama diretamente
`bombchicken-nextos`; o pacote não contém `run.sh` interno, desvio por nome de
firmware nem varredura da tabela global de processos.

Quando esse launcher novo alcança a fase `prepare` declarada, a versão 1.1.1
confere os quatro resíduos conhecidos da instalação 1.0 pelo SHA-256 exato e
move somente os bytes reconhecidos para a quarentena não executável
`.nxlegacy-bombchicken-v1/`, fora do diretório ativo. Em FAT/exFAT que não
preserva o modo não executável, esse resíduo de bytes exatos é removido da
quarentena. Bytes desconhecidos, symlinks e outros tipos são preservados e
bloqueiam a abertura para revisão manual. A migração nomeia apenas `run.sh`,
`es_map.sh`, `es2sdl.awk` e o loader antigo `bombchicken`; nunca varre
processos/outra raiz de ROM e nunca toca `assets/`, `lib/`, `home`, `gamedata/`
ou saves.

Isso cobre instalação limpa e update do PortMaster na mesma raiz ativa de
scripts. Não é possível remover pelo launcher uma cópia antiga visível deixada
em cartão ou raiz muOS inativa. Se a raiz de armazenamento do PortMaster mudou
entre versões, desinstale/remova explicitamente a entrada antiga ou faça uma
instalação limpa antes de usar a entrada nova.

O adaptador compilado continua específico do jogo. Ele mapeia `libmain.so`,
`libunity.so` e `libil2cpp.so` AArch64 originais do dono, oferece a superfície
Android/JNI, EGL/GLES, áudio e input realmente usada e reproduz a ordem nativa:

1. mapear e realocar `libmain` → `libunity` → `libil2cpp`;
2. rodar construtores de `libmain` e depois seu `JNI_OnLoad`;
3. chamar o `NativeLoader.load` registrado, que executa construtores e
   `JNI_OnLoad` reais de `libunity` e `libil2cpp`, nessa ordem;
4. chamar `initJni`, surface-created, surface-changed, foco e resume;
5. executar o loop real de `nativeRender`;
6. na saída, enviar perda de foco e pause antes de fechar input e áudio.

Nenhum entry point, construtor ou estágio nativo é pulado. A migração não finge
que o adaptador comprovado já foi substituído por todos os módulos
compartilhados: o framework universal controla o contrato e o pré-runtime; o
código de compatibilidade Unity permanece em `src/`.

### Quirks específicos e comprovados

Todas as correções nascem desligadas e só são ativadas pelos tokens exatos,
separados por nova linha, que vêm do contrato gerado:

| Token do contrato | Finalidade comprovada |
|---|---|
| `game.bombchicken.menu-cursor-v44` | seta polida no analógico direito para o menu touch-only v44; R3 clica |
| `game.bombchicken.native-pause-v44` | chama `LevelStart.PausePressed()` v44 e o caminho nativo de retomada |
| `game.bombchicken.nonnull-play-games-v44` | entrega objeto JNI vivo onde o Play Games v44 desreferencia serviço opcional |
| `game.bombchicken.present-alpha-one` | preserva RGB visível em compositores que misturam o framebuffer padrão pelo alpha |
| `game.bombchicken.progress-parser-v44` | trata registros `Progress` malformados/finais sem quebrar a troca de fase |
| `game.bombchicken.stencil8-v44` | fornece o stencil pedido pelo caminho de render v44 comprovado |

A seleção gráfica é por capacidade. O adaptador tenta um contexto GLES2 de
propriedade do SDL e só usa EGL cru quando a tentativa falha ou quando um
override explícito de diagnóstico pede isso. Nome de firmware, aparelho ou GPU
não decide o caminho.

### Controles

| Controle | Ação |
|---|---|
| Direcional / analógico esquerdo | mover |
| A | confirmar nos menus; botar bomba na fase |
| B | botar bomba |
| Start | iniciar no título; pausar/despausar na fase |
| Analógico direito | mover a seta nos menus touch-only |
| R3 | clicar com a seta |
| Select + Start | sair pela sequência normal de lifecycle |

Os mapeamentos vêm do framework/SDL do host. O port não inclui GUID fixo nem
override por nome de controle. Permanece um fallback por capacidades reais de
joystick/evdev para portáteis que não aparecem na base GameController do SDL.

### Dados do dono com NXExtract 1.2.6

Somente **Bomb Chicken Android v44 / build 45**, pacote
`com.nitrome.bombchicken`, ABI `arm64-v8a`, corresponde ao contrato exato.
Coloque seu APK legal em `gamedata/` dentro do port instalado e abra o launcher
visível. O NXExtract 1.2.6 confere pacote, hashes das três bibliotecas e o
fingerprint completo da árvore Unity antes de instalar `assets/` e `lib/`
atomicamente.

Não extraia manualmente e não inclua esses arquivos no código-fonte ou ZIP
público. `nxextract-version.txt` registra a evidência aceita e os hashes do
NXExtract sem patches; `extractor.json` é a receita executável.

### Compilar, testar e publicar

O loader público é compilado numa imagem Debian Buster offline e fixada. O
sysroot do alvo é montado somente-leitura para headers SDL2/EGL/GLES; nenhuma
biblioteca de glibc alta do firmware entra no link.

```sh
cd ports/bombchicken
./build.sh
./tests/run-host.sh
```

O gate valida a receita NXExtract, contrato e privacidade, faz dois builds
limpos e compara os bytes. Todos os ELFs construídos são auditados por
arquitetura, interpretador, `DT_NEEDED`, RPATH/RUNPATH e versões de símbolos.
Ele não abre o jogo nem acessa aparelho. O pacote público só é produzido pela
receita determinística do NXRelease depois que os artefatos gerados pelo
framework forem fixados.

Diagnósticos opt-in úteis: `BC_VERBOSE=1`, `BC_LOGCAT=1`, `BC_JNILOG=1`,
`BC_GLLOG=1`, `BC_AUDIO_TRACE=1`, `BC_FPS=1` e o limite de teste
`BC_FRAMES=N`. Nenhum deles é ligado pelo contrato público. O bundle público
determinístico é auditado e reaberto pelo NXRelease 0.2.5.

### Mapa do código

- `src/main.c` — ponte contrato→quirks e lifecycle Unity exato.
- `src/nx_elf.c` — mapeamento ELF Android AArch64, realocações e init arrays.
- `src/jni.c` / `src/android.c` — compatibilidade JNI e serviços Android.
- `src/egl.c` / `src/egl_sdl.c` — superfície EGL/GLES2, present e hooks ETC2.
- `src/input.c` — ponte SDL/Android e correções exatas do gameplay v44.
- `src/audio.c` — caminho de áudio Unity FMOD/OpenSL→SDL.
- `nxport.json` — contrato universal de capacidades e quirks.
- `extractor.json` — receita exata de dados BYO.
- `tests/` — gates host de contrato, extração e ELF sem executar o jogo.

### Licença e créditos

O código de compatibilidade e a integração são GPL-3.0-only; veja `LICENSE` e
`NOTICE.md`. O NXExtract 1.2.6 usa licença MIT; veja
`licenses/NXExtract-MIT.txt`. Créditos das referências de interoperabilidade
estão em `NOTICE.md`. Bomb Chicken e todos os dados do dono continuam sendo
dos respectivos titulares. Este projeto independente não é afiliado nem
endossado por Nitrome, Unity ou Google.
