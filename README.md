# 📈 Inteligencia de Medios Colombia | Powered by Stitch

Este proyecto es un dashboard interactivo desarrollado en **Streamlit** que visualiza la evolución histórica, las tendencias actuales y las proyecciones futuras de la inversión publicitaria en Colombia (1995 – 2031).

## 🚀 Características Principales

- **🏛️ Contexto Histórico**: Análisis de picos de inversión y eventos críticos (Pandemia, Reformas).
- **📺 Valor de la TV**: Storytelling estratégico que defiende el valor absoluto y la confianza de la televisión nacional.
- **📈 Tendencias & Mix**: Visualización dinámica de la mediamorfosis de medios tradicionales a digitales.
- **🧮 Estadística Avanzada**: Matrices de correlación y análisis de dispersión por medio.
- **🔮 Proyecciones**: Modelos de crecimiento proyectados hasta 2031.
- **🎨 Diseño Premium**: Interfaz moderna con efectos de glassmorphism y optimización móvil.

## 🛠️ Tecnologías Utilizadas

- **Python 3.9+**
- **Streamlit**: Framework de la aplicación web.
- **Pandas & Numpy**: Procesamiento y análisis de datos.
- **Plotly**: Gráficas interactivas de alta gama.
- **CSS3 / Glassmorphism**: Estilo visual avanzado y responsivo.

---
## 🌐 Despliegue en Streamlit Cloud

Para desplegar esta aplicación en **Streamlit Cloud** :

1.  **Sube tus archivos a GitHub** (excluyendo `firebase-key.json`).
2.  **Configura los Secretos en Streamlit Cloud**:
    *   En el panel de control de tu aplicación, ve a **Settings** > **Secrets**.
    *   Pega el contenido de tu archivo `firebase-key.json` en este formato:
    ```toml
    [firebase]
    type = "service_account"
    project_id = "tu-proyecto-id"
    private_key_id = "tu-private-key-id"
    private_key = "-----BEGIN PRIVATE KEY-----\n..."
    client_email = "..."
    # etc...
    ```
3.  **Asegúrate de que `requirements.txt` esté presente** para que Streamlit instale todas las librerías automáticamente.

## 📦 Instalación Local

1.  Clona este repositorio:
    ```bash
    git clone https://github.com/TU_USUARIO/dashboard_inversion_publicitaria.git
    cd dashboard_inversion_publicitaria
    ```

2.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

3.  Configura tu clave de Firebase:
    *   Coloca tu archivo `firebase-key.json` en la raíz del proyecto.

4.  Ejecuta la aplicación:
    ```bash
    streamlit run app.py
    ```

## 👩‍💻 Autor
**Luis Miguel López** - *Data Analyst Professional | Marketing & Media Strategy*
[LinkedIn](https://www.linkedin.com/in/luislopezanalytics)

---
*Análisis y Desarrollo impulsado por la metodología de Stitch Analytics.*
