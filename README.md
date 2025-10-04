# Tweakio-Whatsapp Library

This repository provides a developer-friendly toolkit for **WhatsApp automation**, with modular components for building pipelines and advanced automation workflows. This library is designed for developers who want to **automate WhatsApp tasks** efficiently and safely, while leveraging modern automation techniques.

We are also working on a **research paper** that studies WhatsApp security and automation practices. The link to the paper will be added once published.

---

## Features

* **Modern automation stack**: Built on **Playwright (Python)** for reliable browser automation.
* **Modular design**: Includes components like `ChatRoller`, `MessageLoader`, `BrowserIntegrate`, and more.
* **Human-like automation**: Simulates realistic typing and mouse behavior.
* **Extensible selectors**: Priority selector API for handling dynamic UI elements.
* **Document and message handling**: Send and receive different types of messages seamlessly.
* **Template for developers and small businesses**: Build WhatsApp integrations without using the official WhatsApp Business API.

---

## Example Usage

```python
from whatsapp_bot import Whatsapp

# Login via code
session = Whatsapp.login(number="+911234567890", country="IN")

# Logout
session.logout()
```

> This example demonstrates a simple automation pipeline. More advanced integrations can be built using the modular components of the library.

---

## Why Use This Library?

1. Uses **modern technology** (Playwright) for reliable automation.
2. Implements **humanized interactions** to make automation realistic.
3. **Improves on other libraries** by addressing fragile selectors and providing a priority selector API.
4. Provides a **base template** for developers and small businesses to build WhatsApp automation workflows.
5. Supports **advanced functionality** like document handling, profile clickers, and custom message parsing.

---

## Roadmap

* Adding more modules like **ChatRoller**, **MessageLoader**, and **BrowserIntegrate** with anti-detection techniques.
* Expanding **priority selector functionality** for dynamic UI elements.
* Publishing a **research paper** on WhatsApp automation and security.

---

## Contributing

Contributors are welcome! Feel free to:

* Report issues and bugs.
* Suggest improvements.
* Contribute code via pull requests.

---

## License

This project is licensed under the [MIT License](LICENSE).

