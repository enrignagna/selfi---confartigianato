from questionario_app.ui import configure_page, get_risposte, render_header, render_page, render_sidebar


def main():
    configure_page()
    render_header()
    risposte = get_risposte()
    pagina = render_sidebar()
    render_page(pagina, risposte)


if __name__ == "__main__":
    main()
