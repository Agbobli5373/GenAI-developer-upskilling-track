import os
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# --- 1. Define Documents and Metadata ---
# In a real-world scenario, this would come from a database or file system.
documents = [
     # --- HR Policies (for role: "hr") ---
    "HR Policy: The annual leave policy for full-time employees at the Ghana delivery center is set at 21 working days per calendar year, following the completion of the mandatory six-month probationary period. Leave is accrued on a pro-rata basis at a rate of 1.75 days per month. Employees are required to request leave at least two weeks in advance through the company's HR Information System (HRIS) portal, 'BambooHR'. A maximum of 5 unused leave days can be carried over into the first quarter of the subsequent year, after which they will be forfeited. For employees at our European and US offices, the annual leave entitlement is 25 days, in compliance with local labor standards, with similar accrual and request procedures.",

    "HR Policy: Our performance management framework is a bi-annual process designed to foster continuous growth and provide clear feedback. The cycle begins in June with a mid-year check-in and concludes in December with the annual review. The process involves a 360-degree feedback model where employees provide a self-assessment, receive anonymous feedback from peers, and have a comprehensive one-on-one review with their line manager. Performance is evaluated against a set of core company competencies and role-specific Key Performance Indicators (KPIs). The outcomes of this review directly influence salary adjustments, bonus allocations, and consideration for promotion, which are finalized in the first quarter of the following year.",

    "HR Policy: Amalitech is committed to the professional development of its staff and allocates an annual training budget for each department. Employees are encouraged to pursue one major professional certification per year, with the company covering 100% of the examination fees for approved certifications such as AWS Certified Solutions Architect, Certified ScrumMaster (CSM), or PMP. To qualify for sponsorship, the employee must submit a development plan outlining how the certification aligns with their career path and benefits the company. The policy also supports participation in relevant tech conferences and workshops, covering up to 70% of the ticket and travel costs, subject to line manager and HR approval.",

    "HR Policy: The company's Code of Conduct strictly outlines our stance on data privacy and client confidentiality. All employees, upon joining, must complete a mandatory GDPR and data protection training module. Access to client data is granted on a strict need-to-know basis, and the use of production client data in any non-production environment (including development and staging) is strictly forbidden. Any breach of this policy, including unauthorized sharing of internal documents or client information, is considered a serious offense and will lead to disciplinary action, which may include termination of employment. All employees are required to re-certify their understanding of this policy annually.",

    "HR Policy: Amalitech's compensation structure is based on a transparent salary banding system, which is reviewed annually against industry benchmarks in the relevant geographical markets (West Africa, Europe, and North America). Each role is assigned a level, and each level has a defined salary range. Progression within a band is tied to performance, skills acquisition, and experience. In addition to base salary, eligible employees participate in a company-wide bonus scheme tied to both company profitability and individual performance. The company also contributes to a mandatory SSNIT pension fund for Ghanaian employees and offers competitive private pension matching schemes for international staff.",

    # --- Engineering Guidelines (for role: "engineering") ---
    "Engineering Guideline: The established Git workflow for all software projects is GitFlow. All development work must be done on feature branches created from the 'develop' branch. When a feature is complete, a pull request (PR) must be submitted to merge it into 'develop'. Every PR requires a minimum of two approvals from other team members, one of whom must be a Senior Engineer or a Team Lead. The PR must also pass all automated checks in our Azure DevOps CI pipeline, which includes code linting with ESLint/Black, unit tests with a minimum of 80% code coverage, and a clean SonarQube quality gate analysis. Direct pushes to the 'develop' or 'main' branches are disabled and strictly prohibited.",

    "Engineering Guideline: For new backend services, the default architectural pattern is microservices using Python with the FastAPI framework. This choice prioritizes high performance, asynchronous capabilities, and automatic OpenAPI documentation generation. Services should communicate with each other via synchronous RESTful APIs for requests/responses or asynchronously via a message broker like RabbitMQ for event-driven workflows. All services must be containerized using Docker and deployed as part of a Kubernetes cluster on Azure Kubernetes Service (AKS). Each microservice must have its own isolated PostgreSQL database, and direct database-to-database communication is forbidden; all interaction must occur through the API layer.",

    "Engineering Guideline: Security is a core tenet of our development process. Secrets management for all applications must be handled through Azure Key Vault. Under no circumstances should secrets, API keys, or passwords be hardcoded in the source code, configuration files, or committed to the Git repository. Applications should be configured to retrieve these secrets at runtime using managed identities where possible. Furthermore, all third-party dependencies are continuously scanned for known vulnerabilities using Snyk, integrated into our CI pipeline. Any dependency with a high or critical severity vulnerability must be patched or updated before a deployment to production can be approved.",

    "Engineering Guideline: Frontend application development for client-facing projects must adhere to the standardized stack of Next.js 14+ with TypeScript. State management should be implemented using Zustand for its simplicity and minimal boilerplate, while Tailwind CSS is the designated utility-first CSS framework for styling. All components should be developed with accessibility in mind, adhering to WCAG 2.1 AA standards. For data fetching, we leverage SWR or React Query for client-side data and Next.js's built-in data fetching methods for server-side rendering (SSR) and static site generation (SSG) to ensure optimal performance and SEO.",

    "Engineering Guideline: All public-facing APIs must be documented using the OpenAPI 3.0 specification. This documentation should be automatically generated wherever possible, for instance, through FastAPI's native capabilities. The documentation must clearly define all endpoints, expected request/response schemas, authentication methods (typically OAuth2), and potential error codes. This API documentation serves as the contract between the frontend and backend teams and must be kept up-to-date with any changes. The Swagger UI for these APIs should be accessible in our development and staging environments to facilitate easy testing and exploration by developers and QA engineers.",

    # --- Public Announcements (for role: "public") ---
    "Public Announcement: Amalitech is proud to announce it has achieved ISO/IEC 27001:2013 certification, the leading international standard for information security management systems (ISMS). This certification affirms that Amalitech has implemented comprehensive security controls and best practices to protect its corporate and client data against threats. The rigorous audit process, conducted by an independent third-party registrar, validates our commitment to maintaining the highest levels of confidentiality, integrity, and availability for all information assets. This milestone provides our clients and partners with the assurance that their sensitive data is managed in a secure and compliant environment.",

    "Public Announcement: In a significant step to deepen our engagement with the European market, Amalitech has officially opened a new client relations and service delivery office in Berlin, Germany. This expansion is a direct response to the growing demand for our tech services in the DACH region (Germany, Austria, Switzerland) and will serve as a hub for our project management and client success teams. The Berlin office will enable us to provide more localized support, foster closer collaboration with our European clients, and tap into the vibrant local tech talent pool. This strategic move underscores our commitment to being a truly global service provider with a strong local presence.",

    "Public Announcement: Building on the incredible success of our Training Academy, Amalitech is launching a new, specialized program in Data Engineering and Cloud Computing. This intensive 6-month course is designed to equip trainees with in-demand skills in data pipeline construction, ETL processes, cloud architecture on AWS and Azure, and big data technologies like Spark and Kafka. The program was co-developed with industry partners to ensure the curriculum directly addresses the skills gap in the global market. Applications are now open, with the first cohort of 50 trainees scheduled to begin in Q4. This initiative aligns with our mission to cultivate world-class tech talent in West Africa.",

    "Public Announcement: Amalitech has published a new industry whitepaper titled 'Leveraging AI for Sustainable Growth in Emerging Markets.' The report provides an in-depth analysis of how businesses in sectors like agriculture, finance, and healthcare can adopt AI-driven solutions to optimize operations, reduce costs, and create new value streams. The research highlights several case studies and presents a practical framework for AI adoption. This publication is part of our ongoing commitment to thought leadership and our belief in technology's power to drive positive economic and social change. The whitepaper is available for free download on our company website.",

    "Public Announcement: We are excited to announce a strategic partnership with the Meltwater Entrepreneurial School of Technology (MEST Africa). This collaboration will see Amalitech provide technical mentorship, internship opportunities, and curriculum advisory to MEST's portfolio of tech startups. Our senior engineers and project managers will lead workshops on topics ranging from scalable cloud architecture to agile project management. By combining MEST's proven track record in nurturing entrepreneurs with Amalitech's deep expertise in service delivery and software engineering, we aim to strengthen the startup ecosystem across Africa and accelerate the growth of the next generation of tech innovators."
]

metadatas = [
    {"role": "hr"},
    {"role": "hr"},
    {"role": "engineering"},
    {"role": "engineering"},
    {"role": "public"},
    {"role": "public"}
]

# --- 2. Initialize Embeddings and Vector Store ---
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vector_store = Chroma(
    collection_name="rag-chroma",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# --- 3. Add Documents to the Vector Store ---
vector_store.add_texts(
    texts=documents,
    metadatas=metadatas
)

print("Data ingestion complete.")