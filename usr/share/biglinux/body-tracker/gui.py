#####################
# Início do código da dica de ferramenta / Tooltip code start
#####################
tkTooltip = tk.Tk()

# Exibir texto usando tk / Show text using tk
async def tkTooltipChange(text, color, bg, mouseX, mouseY):
    # Criar a janela da tooltip se ainda não foi criada
    # Create the tooltip window if it hasn't been created yet
    global tkTooltip
    if not tkTooltip:
        tkTooltip = tk.Toplevel()
        tkTooltip.transient(root) # Tornar a janela de tooltip "filha" da janela principal / Make the tooltip window a "child" of the main window
    
    # Desabilitar a borda da janela / Disable window border
    tkTooltip.wm_overrideredirect(True)


    # Configurar variáveis para a dica de ferramenta
    # Set up variables for the tooltip
    tooltipText = text
    tooltipTextColor = color
    tooltipBgColor = bg
    tooltipFontSize = 20
    if text == "":
        tooltipWidth = 20
        tooltipHeight = 20
    elif text == "hide":
        tooltipWidth = 0
        tooltipHeight = 0
    else:
        tooltipWidth = len(text) * tooltipFontSize
        tooltipHeight = tooltipFontSize + 14

    # Definir posição e tamanho da dica de ferramenta
    # Set tooltip position and size
    if mouseX > 300:
        mouseX = mouseX - tooltipWidth - 40
    else:
        mouseX = mouseX + tooltipWidth + 40

    if mouseY > 180:
        mouseY = mouseY - tooltipHeight - 40
    else:
        mouseY = mouseY + tooltipHeight + 40


    tkTooltip.wm_geometry(f"{tooltipWidth}x{tooltipHeight}+{mouseX}+{mouseY}")
    
    # Remover o widget Label anterior antes de criar um novo
    # Hide all the children of a widget. It is used
    # when the user wants to hide the tooltip.
    for child in tkTooltip.winfo_children():
        child.destroy()


    # Configurar e aplicar fonte e estilo da dica de ferramenta
    # Configure and apply font and style for the tooltip
    l = tk.Label(tkTooltip, font=("Ubuntu Mono", tooltipFontSize))
    l.pack(expand=True)
    l.config(text=tooltipText, fg=tooltipTextColor, bg=tooltipBgColor, width=tooltipWidth, height=tooltipHeight, borderwidth=2, highlightbackground=tooltipTextColor, highlightthickness=2)
    
    # Configurar aparência da dica de ferramenta
    # Configure tooltip appearance
    tkTooltip.configure(background=bg)

    # Atualizar dica de ferramenta / Update tooltip
    tkTooltip.update()


# Exibir texto no centro da tela / Display text in the center of the screen
async def tkTooltipChangeCenter(text, color, bg):
    # Configurar variáveis para a dica de ferramenta
    # Set up variables for the tooltip
    tooltipText = text
    tooltipTextColor = color
    tooltipBgColor = bg
    tooltipFontSize = 20
    tooltipWidth = int(len(text) * tooltipFontSize / 2)
    tooltipHeight = tooltipFontSize * 2 + 20
    mouseX = int((tkTooltip.winfo_screenwidth() / 2) - tooltipWidth / 2)
    mouseY = int((tkTooltip.winfo_screenheight() / 2) - tooltipHeight / 2)


    # Desabilitar a borda da janela / Disable window border
    tkTooltip.wm_overrideredirect(True)

    tkTooltip.geometry(
        f"{tooltipWidth}x{tooltipHeight}+{mouseX}+{mouseY}".format(
            tkTooltip.winfo_screenwidth(), tkTooltip.winfo_screenheight()
        )
    )
    # Configurar aparência da dica de ferramenta
    # Configure tooltip appearance
    tkTooltip.configure(background=bg)

    # Configurar e aplicar fonte
    # Configure and apply font
    l = tk.Label(font=("Ubuntu Mono", tooltipFontSize))
    l.pack(expand=True)
    l.config(text=tooltipText, fg=tooltipTextColor, bg=tooltipBgColor, width=tooltipWidth, height=tooltipHeight, borderwidth=2, highlightbackground=color, highlightthickness=2)
    # Atualizar dica de ferramenta / Update tooltip
    tkTooltip.update()