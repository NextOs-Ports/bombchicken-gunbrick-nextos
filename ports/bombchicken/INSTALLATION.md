# Installation / Instalação

The public package contains no Bomb Chicken game data. You must own the
Android v44/build 45 release for `arm64-v8a`.

## English

1. Extract the complete release ZIP into your firmware's **ports** directory,
   preserving this layout:

   ```text
   <ROMS>/ports/Bomb Chicken.sh
   <ROMS>/ports/bombchicken/
   ├── bombchicken-nextos
   ├── nxbootstrap-0.5.1.sh
   ├── nxbootstrap.sh
   ├── nxdeployment.json
   ├── nxport.json
   ├── migrate-legacy-overlay.sh
   ├── extractor.json
   ├── nxextract/
   └── gamedata/README.txt
   ```

   `<ROMS>` is the root chosen by your firmware; no particular absolute path
   is required. A PortMaster frontend may place the visible `Bomb Chicken.sh`
   in its normal scripts directory while keeping `bombchicken/` in the ports
   data directory. Keep both bootstrap files: the launcher selects the
   versioned 0.5.1 implementation, while `nxbootstrap.sh` is the byte-identical
   compatibility copy.

   For an upgrade from 1.0, use PortMaster on the same active scripts/storage
   root. The first launch through the new entry quarantines only the four exact,
   hash-allowlisted legacy files and preserves all owner data and saves. A
   modified legacy file or symlink is left untouched and blocks launch for
   manual review. Exact residues are removed only when FAT/exFAT cannot retain a
   non-executable quarantine mode. The package does not scan or alter an
   inactive card/root; if you moved between the mmc and sdcard roots on muOS,
   explicitly uninstall or remove the old menu entry there, or perform a clean
   installation.

2. Put the **APK you legally own** in
   `<ROMS>/ports/bombchicken/gamedata/`. The file name does not matter.

3. Start **Bomb Chicken** from the Ports menu. NXExtract 1.2.6 accepts only the
   exact `com.nitrome.bombchicken` v44/build 45 AArch64 payload, validates all
   native libraries and the complete Unity asset tree, then publishes the
   data atomically. Later starts go directly to the game.

4. Your APK is never deleted. After a successful install you may remove it
   from the card to save space, but retain your lawful copy for reinstalls.

Do not create `run.sh`, unpack the APK by hand, copy Android libraries into the
public ZIP or edit `nxdeployment.json`. The latter is a static package receipt,
not mutable runtime state.

### Controls

D-pad/left stick moves; A confirms or places a bomb; B places a bomb; Start
pauses/resumes; the right stick moves the pointer in touch-only menus and R3
clicks. Select + Start exits through focus-lost and native pause.

### Diagnosing a launch

There are four observable boundaries:

1. missing `nxdeployment.json`: the package installer/extractor did not
   deliver the complete release;
2. receipt present but no new `bombchicken-launcher-error.*.log` or
   `debug.log`: there is no durable proof that the launcher's early trap was
   reached; inspect frontend/PortMaster placement, shell interpreter/parse,
   writable storage, SIGKILL and power loss before assigning a cause;
3. `bombchicken-launcher-error.*.log`: failure before the runtime started;
4. `debug.log`: runtime phases after bootstrap; `nxextract.log` covers the
   owner-data installer.

A script cannot log before the operating system or frontend executes it. If
the receipt is present and neither launcher nor runtime log exists, start at
the frontend/launcher boundary rather than treating silence as a game crash.

## Português

O pacote público não contém dados de Bomb Chicken. Você precisa possuir a
versão Android v44/build 45 para `arm64-v8a`.

1. Extraia o ZIP completo da release na pasta **ports** do seu firmware,
   preservando a estrutura:

   ```text
   <ROMS>/ports/Bomb Chicken.sh
   <ROMS>/ports/bombchicken/
   ├── bombchicken-nextos
   ├── nxbootstrap-0.5.1.sh
   ├── nxbootstrap.sh
   ├── nxdeployment.json
   ├── nxport.json
   ├── migrate-legacy-overlay.sh
   ├── extractor.json
   ├── nxextract/
   └── gamedata/README.txt
   ```

   `<ROMS>` é a raiz escolhida pelo firmware; nenhum caminho absoluto
   específico é obrigatório. Um frontend PortMaster pode manter o
   `Bomb Chicken.sh` visível na pasta normal de scripts e `bombchicken/` na
   pasta de dados dos ports. Mantenha os dois bootstraps: o launcher seleciona
   a implementação 0.5.1 versionada e `nxbootstrap.sh` é a cópia de
   compatibilidade byte-idêntica.

   Ao atualizar da 1.0, use o PortMaster na mesma raiz ativa de scripts/dados. A
   primeira abertura pela entrada nova põe em quarentena somente os quatro
   arquivos legados exatos da allowlist de SHA-256 e preserva dados do dono e
   saves. Arquivo legado modificado ou symlink não é tocado e bloqueia a abertura
   para revisão manual. Resíduos exatos só são removidos quando FAT/exFAT não
   consegue manter a quarentena sem permissão de execução. O pacote não varre
   nem altera cartão/raiz inativa; se você mudou entre as raízes mmc e sdcard do
   muOS, desinstale ou remova explicitamente a entrada antiga, ou faça uma
   instalação limpa.

2. Coloque o **APK que você possui legalmente** em
   `<ROMS>/ports/bombchicken/gamedata/`. O nome do arquivo não importa.

3. Abra **Bomb Chicken** no menu Ports. O NXExtract 1.2.6 aceita apenas o
   payload AArch64 exato `com.nitrome.bombchicken` v44/build 45, valida todas
   as bibliotecas e a árvore Unity completa e só então publica os dados
   atomicamente. Nas próximas aberturas o jogo inicia direto.

4. Seu APK nunca é apagado. Depois da instalação você pode removê-lo do cartão
   para liberar espaço, mas guarde sua cópia legal para reinstalações.

Não crie `run.sh`, não extraia o APK manualmente, não coloque bibliotecas
Android no ZIP público e não edite `nxdeployment.json`. Ele é um receipt
estático do pacote, não estado mutável do runtime.

### Controles

Direcional/analógico esquerdo move; A confirma ou bota bomba; B bota bomba;
Start pausa/despausa; o analógico direito move a seta nos menus touch-only e
R3 clica. Select + Start sai pela perda de foco e pause nativos.

### Diagnóstico de abertura

Há quatro fronteiras observáveis:

1. `nxdeployment.json` ausente: instalador/extrator do pacote não entregou a
   release completa;
2. receipt presente, mas sem novo `bombchicken-launcher-error.*.log` nem
   `debug.log`: não há prova durável de que o trap inicial do launcher foi
   alcançado; confira posição/registro no frontend ou PortMaster,
   interpretador/sintaxe do shell, armazenamento gravável, SIGKILL e queda de
   energia antes de afirmar a causa;
3. `bombchicken-launcher-error.*.log`: falha antes de iniciar o runtime;
4. `debug.log`: fases do runtime depois do bootstrap; `nxextract.log` registra
   o instalador dos dados do dono.

Um script não consegue registrar nada antes de o sistema ou frontend executá-lo.
Se o receipt existe e não há log de launcher nem de runtime, comece pela
fronteira frontend/launcher em vez de classificar o silêncio como crash do jogo.
