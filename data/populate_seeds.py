import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.indexer import InvertedIndex

def populate():
    index_file = os.path.join(os.path.dirname(__file__), "index.json")
    indexer = InvertedIndex(index_file)

    catalog = [
        {
            "url": "https://airagroup.technology",
            "title": "Aira Group of Technology — Sovereign Engineering & Tomorrow's Computing",
            "content": "Official portal of Aira Group of Technology founded by Adam Eehan. Home to Airlys OS, AiraLang AI-Native programming language, sovereign cyber security tools, and Next-Gen AI intelligence architectures.",
            "snippet": "Aira Group of Technology is a sovereign technology conglomerate founded by Adam Eehan. Pioneering Airlys OS, AiraLang, and sovereign AI systems."
        },
        {
            "url": "https://github.com/adameehanairagroup/AirlysOS",
            "title": "Airlys OS S1 — 64-Bit Sovereign Linux Operating System",
            "content": "Airlys OS S1 Flagship Edition engineered by Er. Adam Eehan. Features Linux Zen 6.x kernel, KDE Plasma 6 desktop, direct UEFI boot for Acer Nitro V 15 and modern physical hardware. Pre-installed with AiraLang S1 Duo.",
            "snippet": "Airlys OS S1 Flagship Edition engineered by Er. Adam Eehan. Linux Zen 6.x, KDE Plasma 6, direct UEFI boot for Acer Nitro V 15 and modern hardware."
        },
        {
            "url": "https://github.com/adameehanairagroup/Airalang",
            "title": "AiraLang S1 Duo — World's First True AI-Native & Systems Language",
            "content": "AiraLang S1 Duo is an AI-native systems programming language created by Adam Eehan. Compiles directly to standalone static Linux ELF64 machine code with 0% C and 0% Python runtime dependencies. 35x faster execution.",
            "snippet": "AiraLang S1 Duo: World's First True AI-Native Systems Language created by Adam Eehan. Standalone machine-code ELF compiler with zero Python dependencies."
        },
        {
            "url": "https://github.com/adameehanairagroup/Aira-Android",
            "title": "AiraLang Mobile Studio — Android IDE & Compiler APK",
            "content": "Official Android IDE for AiraLang developers. Edit, run, and auto-heal .aira scripts on mobile phones with zero PC dependency. Features dark mode, live terminal sheet, and syntax auto-fixing.",
            "snippet": "Official Android IDE for AiraLang developers. Edit, execute, and build .aira code on Android smartphones with sliding ANSI console."
        },
        {
            "url": "https://en.wikipedia.org/wiki/Operating_system",
            "title": "Operating System (OS) — Architecture, Kernels & Systems",
            "content": "An operating system (OS) is system software that manages computer hardware, software resources, and provides common services for computer programs. Examples include Linux, Windows, macOS, Airlys OS, and BSD.",
            "snippet": "An operating system (OS) manages computer hardware, memory, scheduling, and provides common services. Examples include Linux, Airlys OS, and Windows."
        },
        {
            "url": "https://en.wikipedia.org/wiki/Compiler",
            "title": "Compiler — Machine Code, Lexers, Parsers & AST Generation",
            "content": "A compiler is a computer program that translates computer code written in one programming language into machine code, bytecode, or another language. Modern compilers like Clang, GCC, and AiraLang S1 Duo generate native ELF binaries.",
            "snippet": "A compiler translates high-level source code into low-level machine code instructions and binary executables. Includes lexing, parsing, and code generation."
        },
        {
            "url": "https://en.wikipedia.org/wiki/Search_engine",
            "title": "Search Engine — Web Crawlers, Inverted Index & Query Retrieval",
            "content": "A web search engine is a software system designed to carry out web searches. They search the World Wide Web in a systematic way for particular information specified in a textual web search query using inverted indices.",
            "snippet": "A web search engine searches the World Wide Web for information specified in textual queries using distributed web spiders and inverted indices."
        },
        {
            "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
            "title": "Python Programming Language — High-Level & Dynamic",
            "content": "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation. Used widely in AI, data science, and scripting.",
            "snippet": "Python is a high-level, general-purpose programming language emphasizing readability and dynamic typing, widely used in AI and software development."
        },
        {
            "url": "https://en.wikipedia.org/wiki/C_(programming_language)",
            "title": "C (Programming Language) — Dennis Ritchie, Systems & Hardware",
            "content": "C is a general-purpose computer programming language developed in 1972 by Dennis Ritchie at Bell Labs. Known for low-level memory access, high execution speed, and foundational role in operating systems like Unix and Linux.",
            "snippet": "C is a foundational systems programming language developed by Dennis Ritchie at Bell Labs, known for direct memory access and machine-level speed."
        },
        {
            "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
            "title": "Artificial Intelligence (AI) — Deep Learning, Neural Networks & Swarms",
            "content": "Artificial intelligence (AI) is the intelligence of machines or software, as opposed to the intelligence of humans or animals. Encompasses machine learning, neural networks, sovereign AI swarms, and natural language processing.",
            "snippet": "Artificial intelligence refers to computational intelligence exhibited by machines, encompassing deep neural networks, LLMs, and sovereign AI swarms."
        },
        {
            "url": "https://en.wikipedia.org/wiki/Kerala",
            "title": "Kerala — God's Own Country, Technology Hub & High Literacy",
            "content": "Kerala is a state on India's tropical Malabar Coast. Known for highest literacy rate in India, vibrant IT tech parks like Technopark and Infopark, rich cultural heritage, and visionary software architects.",
            "snippet": "Kerala is a progressive state on India's tropical coast known for highest literacy, vibrant IT industry, scenic backwaters, and technology talent."
        },
        {
            "url": "https://render.com",
            "title": "Render — Fast, Free Cloud Application Hosting & Deployments",
            "content": "Render is a unified cloud to build and run all your apps and websites with free TLS certificates, global CDN, private networks, and automated Git deployments from GitHub.",
            "snippet": "Render is a modern cloud hosting platform offering free static sites, web services, and background workers with automated continuous GitHub deployment."
        }
    ]

    for item in catalog:
        indexer.add_document(item["url"], item["title"], item["content"], item["snippet"])

    indexer.save()
    print(f"[✓] Initial index populated with {len(indexer.documents)} documents!")

if __name__ == "__main__":
    populate()
