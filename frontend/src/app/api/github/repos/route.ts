import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth-options";
import { NextResponse } from "next/server";

// Framework detection from package.json dependencies
const JS_FRAMEWORKS: Record<string, string> = {
  "next": "Next.js",
  "react": "React",
  "express": "Express",
  "@angular/core": "Angular",
  "vue": "Vue.js",
  "nuxt": "Nuxt.js",
  "@nestjs/core": "NestJS",
  "svelte": "Svelte",
  "@sveltejs/kit": "SvelteKit",
  "gatsby": "Gatsby",
  "remix": "Remix",
  "fastify": "Fastify",
  "koa": "Koa",
  "hapi": "Hapi",
  "electron": "Electron",
  "react-native": "React Native",
  "expo": "Expo",
  "@ionic/angular": "Ionic",
  "vite": "Vite",
  "webpack": "Webpack",
  "tailwindcss": "Tailwind CSS",
  "prisma": "Prisma",
  "mongoose": "MongoDB",
  "typeorm": "TypeORM",
  "sequelize": "Sequelize",
  "socket.io": "Socket.io",
  "graphql": "GraphQL",
  "@apollo/server": "Apollo GraphQL",
  "three": "Three.js",
};

// Python framework detection
const PYTHON_FRAMEWORKS: Record<string, string> = {
  "django": "Django",
  "flask": "Flask",
  "fastapi": "FastAPI",
  "streamlit": "Streamlit",
  "tornado": "Tornado",
  "pyramid": "Pyramid",
  "bottle": "Bottle",
  "starlette": "Starlette",
  "aiohttp": "aiohttp",
  "celery": "Celery",
  "pandas": "Pandas",
  "numpy": "NumPy",
  "tensorflow": "TensorFlow",
  "pytorch": "PyTorch",
  "torch": "PyTorch",
  "scikit-learn": "Scikit-learn",
  "keras": "Keras",
  "opencv": "OpenCV",
  "matplotlib": "Matplotlib",
  "sqlalchemy": "SQLAlchemy",
  "alembic": "Alembic",
};

// Java/Kotlin framework detection (from pom.xml or build.gradle)
const JAVA_FRAMEWORKS: Record<string, string> = {
  "spring-boot": "Spring Boot",
  "spring-webflux": "Spring WebFlux",
  "spring-data": "Spring Data",
  "spring-security": "Spring Security",
  "spring-cloud": "Spring Cloud",
  "quarkus": "Quarkus",
  "micronaut": "Micronaut",
  "hibernate": "Hibernate",
  "ktor": "Ktor",
};

// Special config files that indicate frameworks
const FRAMEWORK_CONFIG_FILES: Record<string, string> = {
  "next.config.js": "Next.js",
  "next.config.ts": "Next.js",
  "next.config.mjs": "Next.js",
  "angular.json": "Angular",
  "vue.config.js": "Vue.js",
  "nuxt.config.js": "Nuxt.js",
  "nuxt.config.ts": "Nuxt.js",
  "svelte.config.js": "SvelteKit",
  "gatsby-config.js": "Gatsby",
  "remix.config.js": "Remix",
  "vite.config.js": "Vite",
  "vite.config.ts": "Vite",
  "tailwind.config.js": "Tailwind CSS",
  "tailwind.config.ts": "Tailwind CSS",
  "prisma/schema.prisma": "Prisma",
  "docker-compose.yml": "Docker Compose",
  "docker-compose.yaml": "Docker Compose",
  "Dockerfile": "Docker",
  ".github/workflows": "GitHub Actions",
  "Jenkinsfile": "Jenkins",
  ".gitlab-ci.yml": "GitLab CI",
  "vercel.json": "Vercel",
  "netlify.toml": "Netlify",
  "fly.toml": "Fly.io",
  "railway.json": "Railway",
};

interface DetectedTech {
  name: string;
  type: "language" | "framework" | "library" | "tool" | "database" | "ci/cd";
  path?: string;
}

async function fetchFileContent(
  repoFullName: string,
  filePath: string,
  accessToken: string
): Promise<string | null> {
  try {
    const res = await fetch(
      `https://api.github.com/repos/${repoFullName}/contents/${filePath}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          Accept: "application/vnd.github.v3+json",
        },
      }
    );

    if (!res.ok) return null;

    const data = await res.json();
    if (data.content) {
      // Content is base64 encoded
      return Buffer.from(data.content, "base64").toString("utf-8");
    }
    return null;
  } catch {
    return null;
  }
}

function detectJSFrameworks(packageJson: any): DetectedTech[] {
  const detected: DetectedTech[] = [];
  const deps = {
    ...packageJson.dependencies,
    ...packageJson.devDependencies,
  };

  for (const [pkg, framework] of Object.entries(JS_FRAMEWORKS)) {
    if (deps[pkg]) {
      const type = ["Next.js", "React", "Angular", "Vue.js", "Svelte", "Express", "NestJS", "Fastify"].includes(framework)
        ? "framework"
        : "library";
      detected.push({ name: framework, type });
    }
  }

  return detected;
}

function detectPythonFrameworks(requirements: string): DetectedTech[] {
  const detected: DetectedTech[] = [];
  const lines = requirements.toLowerCase().split("\n");

  for (const [pkg, framework] of Object.entries(PYTHON_FRAMEWORKS)) {
    if (lines.some(line => line.startsWith(pkg) || line.includes(`/${pkg}`) || line.includes(`${pkg}==`) || line.includes(`${pkg}>=`))) {
      const type = ["Django", "Flask", "FastAPI", "Streamlit", "Tornado"].includes(framework)
        ? "framework"
        : "library";
      detected.push({ name: framework, type });
    }
  }

  return detected;
}

function detectJavaFrameworks(buildFile: string): DetectedTech[] {
  const detected: DetectedTech[] = [];
  const content = buildFile.toLowerCase();

  for (const [pkg, framework] of Object.entries(JAVA_FRAMEWORKS)) {
    if (content.includes(pkg)) {
      detected.push({ name: framework, type: "framework" });
    }
  }

  return detected;
}

async function detectTechStack(
  repoFullName: string,
  defaultBranch: string,
  accessToken: string
): Promise<{
  languages: string[];
  frameworks: string[];
  tools: string[];
  allTech: DetectedTech[];
  configFiles: string[];
}> {
  const allTech: DetectedTech[] = [];
  const configFiles: string[] = [];
  const languagesFound = new Set<string>();
  const frameworksFound = new Set<string>();
  const toolsFound = new Set<string>();

  try {
    // Get file tree
    const treeRes = await fetch(
      `https://api.github.com/repos/${repoFullName}/git/trees/${defaultBranch}?recursive=1`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          Accept: "application/vnd.github.v3+json",
        },
      }
    );

    if (!treeRes.ok) {
      return { languages: [], frameworks: [], tools: [], allTech: [], configFiles: [] };
    }

    const treeData = await treeRes.json();
    const files: string[] = treeData.tree
      ?.filter((item: any) => item.type === "blob")
      ?.map((item: any) => item.path) || [];

    // Check for framework config files
    for (const filePath of files) {
      const fileName = filePath.split("/").pop() || "";

      // Check special config files
      for (const [configFile, techName] of Object.entries(FRAMEWORK_CONFIG_FILES)) {
        if (filePath === configFile || filePath.endsWith(`/${configFile}`) || fileName === configFile) {
          if (!frameworksFound.has(techName) && !toolsFound.has(techName)) {
            const type = ["Docker", "Docker Compose", "GitHub Actions", "Jenkins", "GitLab CI", "Vercel", "Netlify"].includes(techName)
              ? "tool"
              : "framework";
            allTech.push({ name: techName, type, path: filePath });
            if (type === "tool") toolsFound.add(techName);
            else frameworksFound.add(techName);
          }
        }
      }
    }

    // Find and parse package.json files
    const packageJsonFiles = files.filter(f => f.endsWith("package.json"));
    for (const pkgPath of packageJsonFiles.slice(0, 3)) { // Limit to 3 to avoid rate limits
      const content = await fetchFileContent(repoFullName, pkgPath, accessToken);
      if (content) {
        try {
          const pkg = JSON.parse(content);
          configFiles.push(pkgPath);

          // Detect language
          const hasTsConfig = files.some(f => {
            const dir = pkgPath.includes("/") ? pkgPath.substring(0, pkgPath.lastIndexOf("/")) : "";
            const tsPath = dir ? `${dir}/tsconfig.json` : "tsconfig.json";
            return f === tsPath;
          });

          const lang = hasTsConfig ? "TypeScript" : "JavaScript";
          if (!languagesFound.has(lang)) {
            languagesFound.add(lang);
            allTech.push({ name: lang, type: "language", path: pkgPath });
          }

          // Detect frameworks
          const jsFrameworks = detectJSFrameworks(pkg);
          for (const tech of jsFrameworks) {
            if (!frameworksFound.has(tech.name)) {
              frameworksFound.add(tech.name);
              allTech.push({ ...tech, path: pkgPath });
            }
          }
        } catch {}
      }
    }

    // Find and parse requirements.txt files
    const requirementsFiles = files.filter(f => f.endsWith("requirements.txt"));
    for (const reqPath of requirementsFiles.slice(0, 3)) {
      const content = await fetchFileContent(repoFullName, reqPath, accessToken);
      if (content) {
        configFiles.push(reqPath);

        if (!languagesFound.has("Python")) {
          languagesFound.add("Python");
          allTech.push({ name: "Python", type: "language", path: reqPath });
        }

        const pyFrameworks = detectPythonFrameworks(content);
        for (const tech of pyFrameworks) {
          if (!frameworksFound.has(tech.name)) {
            frameworksFound.add(tech.name);
            allTech.push({ ...tech, path: reqPath });
          }
        }
      }
    }

    // Find and parse pyproject.toml
    const pyprojectFiles = files.filter(f => f.endsWith("pyproject.toml"));
    for (const pyPath of pyprojectFiles.slice(0, 2)) {
      const content = await fetchFileContent(repoFullName, pyPath, accessToken);
      if (content) {
        configFiles.push(pyPath);

        if (!languagesFound.has("Python")) {
          languagesFound.add("Python");
          allTech.push({ name: "Python", type: "language", path: pyPath });
        }

        // Simple detection from pyproject.toml
        const pyFrameworks = detectPythonFrameworks(content);
        for (const tech of pyFrameworks) {
          if (!frameworksFound.has(tech.name)) {
            frameworksFound.add(tech.name);
            allTech.push({ ...tech, path: pyPath });
          }
        }
      }
    }

    // Check pom.xml for Java projects
    const pomFiles = files.filter(f => f.endsWith("pom.xml"));
    for (const pomPath of pomFiles.slice(0, 2)) {
      const content = await fetchFileContent(repoFullName, pomPath, accessToken);
      if (content) {
        configFiles.push(pomPath);

        if (!languagesFound.has("Java")) {
          languagesFound.add("Java");
          allTech.push({ name: "Java", type: "language", path: pomPath });
        }

        const javaFrameworks = detectJavaFrameworks(content);
        for (const tech of javaFrameworks) {
          if (!frameworksFound.has(tech.name)) {
            frameworksFound.add(tech.name);
            allTech.push({ ...tech, path: pomPath });
          }
        }
      }
    }

    // Check build.gradle for Java/Kotlin projects
    const gradleFiles = files.filter(f => f.endsWith("build.gradle") || f.endsWith("build.gradle.kts"));
    for (const gradlePath of gradleFiles.slice(0, 2)) {
      const content = await fetchFileContent(repoFullName, gradlePath, accessToken);
      if (content) {
        configFiles.push(gradlePath);

        const lang = gradlePath.endsWith(".kts") ? "Kotlin" : "Java";
        if (!languagesFound.has(lang)) {
          languagesFound.add(lang);
          allTech.push({ name: lang, type: "language", path: gradlePath });
        }

        const javaFrameworks = detectJavaFrameworks(content);
        for (const tech of javaFrameworks) {
          if (!frameworksFound.has(tech.name)) {
            frameworksFound.add(tech.name);
            allTech.push({ ...tech, path: gradlePath });
          }
        }
      }
    }

    // Detect other languages by config files
    const otherConfigs: Record<string, { language: string; runtime: string }> = {
      "go.mod": { language: "Go", runtime: "Go" },
      "Cargo.toml": { language: "Rust", runtime: "Rust" },
      "Gemfile": { language: "Ruby", runtime: "Ruby" },
      "composer.json": { language: "PHP", runtime: "PHP" },
      "pubspec.yaml": { language: "Dart", runtime: "Flutter" },
      "mix.exs": { language: "Elixir", runtime: "Elixir" },
    };

    for (const [configFile, info] of Object.entries(otherConfigs)) {
      if (files.some(f => f.endsWith(configFile)) && !languagesFound.has(info.language)) {
        languagesFound.add(info.language);
        allTech.push({ name: info.language, type: "language" });
        configFiles.push(files.find(f => f.endsWith(configFile))!);
      }
    }

    // Check for Jupyter notebooks
    if (files.some(f => f.endsWith(".ipynb")) && !languagesFound.has("Jupyter Notebook")) {
      languagesFound.add("Jupyter Notebook");
      allTech.push({ name: "Jupyter Notebook", type: "language" });
    }

    // Sort: languages first, then frameworks, then tools
    allTech.sort((a, b) => {
      const order = { language: 0, framework: 1, library: 2, database: 3, tool: 4, "ci/cd": 5 };
      return (order[a.type] || 99) - (order[b.type] || 99);
    });

    return {
      languages: Array.from(languagesFound),
      frameworks: Array.from(frameworksFound),
      tools: Array.from(toolsFound),
      allTech,
      configFiles,
    };
  } catch (error) {
    console.error(`Error detecting tech stack for ${repoFullName}:`, error);
    return { languages: [], frameworks: [], tools: [], allTech: [], configFiles: [] };
  }
}

export async function GET() {
  const session = await getServerSession(authOptions);

  if (!session?.accessToken) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  const res = await fetch("https://api.github.com/user/repos?per_page=100&sort=updated", {
    headers: {
      Authorization: `Bearer ${session.accessToken}`,
    },
  });

  const repos = await res.json();

  if (!Array.isArray(repos)) {
    return NextResponse.json(repos);
  }

  // Fetch tech stack detection for each repo in parallel
  const reposWithTechStack = await Promise.all(
    repos.map(async (repo: any) => {
      const { languages, frameworks, tools, allTech, configFiles } = await detectTechStack(
        repo.full_name,
        repo.default_branch || "main",
        session.accessToken as string
      );

      return {
        ...repo,
        // Primary display
        detectedLanguage: languages[0] || repo.language || null,
        detectedFramework: frameworks[0] || null,
        // All detected
        languages,
        frameworks,
        tools,
        allTech,
        configFiles,
        // For backward compatibility
        allDetectedLanguages: languages.length > 0 ? languages : (repo.language ? [repo.language] : []),
      };
    })
  );

  return NextResponse.json(reposWithTechStack);
}
