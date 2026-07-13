"use client";

import Image from "next/image";

import WasteClassifier from "@/components/WasteClassifier";

export default function Home() {
  return (
    <main>
      <header className="topbar">
        <a className="brand" href="#inicio" aria-label="EcoSorter inicio">
  <Image
    className="brand-logo"
    src="/ecosorter-logo.png"
    alt="Logo EcoSorter"
    width={48}
    height={48}
    priority
  />
  <span>EcoSorter</span>
</a>

        <nav className="navigation" aria-label="Navegación principal">
          <a href="#como-funciona">¿Cómo funciona?</a>
          <a href="#clasificador">Clasificador</a>
          <a href="#impacto">Impacto</a>
        </nav>

        <a className="header-button" href="#clasificador">
          Iniciar clasificación
        </a>
      </header>

      <section className="hero" id="inicio">
        <div className="hero-content">
          <span className="eyebrow">AGENTE VISUAL INTELIGENTE</span>

          <h1>
            Clasifica tus residuos
            <span> de forma simple y responsable.</span>
          </h1>

          <p>
            Muestra un residuo frente a la cámara y EcoSorter te ayudará a
            identificar el contenedor adecuado y cómo prepararlo para reciclar.
          </p>

          <div className="hero-actions">
            <a className="primary-button" href="#clasificador">
              Clasificar un residuo
            </a>

            <a className="secondary-button" href="#como-funciona">
              Ver cómo funciona
            </a>
          </div>

          <div className="hero-tags">
            <span>♻ Reciclaje responsable</span>
            <span>◉ Guía en tiempo real</span>
            <span>✓ Fácil de usar</span>
          </div>
        </div>

        <div className="hero-card" aria-hidden="true">
          <div className="hero-card-glow"></div>

          <div className="floating-card card-top">
            <span className="floating-icon">♻</span>
            <div>
              <strong>Reciclable</strong>
              <small>Botella plástica</small>
            </div>
          </div>

          <div className="eco-illustration">
            <div className="eco-circle">♻</div>
            <span className="sparkle sparkle-one">✦</span>
            <span className="sparkle sparkle-two">✦</span>
            <span className="leaf leaf-one">●</span>
            <span className="leaf leaf-two">●</span>
          </div>

          <div className="floating-card card-bottom">
            <span className="floating-icon yellow-icon">✓</span>
            <div>
              <strong>Acción sugerida</strong>
              <small>Lavar y depositar en blanco</small>
            </div>
          </div>
        </div>
      </section>

      <section className="steps-section" id="como-funciona">
        <div className="section-heading">
          <span className="eyebrow">PROCESO SENCILLO</span>
          <h2>Reciclar correctamente solo toma tres pasos</h2>
          <p>
            EcoSorter combina visión artificial e inteligencia multimodal para
            ayudarte a tomar mejores decisiones al separar tus residuos.
          </p>
        </div>

        <div className="steps-grid">
          <article className="step-card">
            <span className="step-number">01</span>
            <div className="step-icon">◉</div>
            <h3>Muestra el objeto</h3>
            <p>
              Ubica el residuo frente a la cámara para que el sistema pueda
              analizarlo.
            </p>
          </article>

          <article className="step-card">
            <span className="step-number">02</span>
            <div className="step-icon">⌁</div>
            <h3>Analizamos el residuo</h3>
            <p>
              El agente visual reconoce el material y evalúa información útil
              para su clasificación.
            </p>
          </article>

          <article className="step-card">
            <span className="step-number">03</span>
            <div className="step-icon">♻</div>
            <h3>Recibe una recomendación</h3>
            <p>
              Conoce el contenedor correcto y los pasos de preparación antes de
              desecharlo.
            </p>
          </article>
        </div>
      </section>

      <section className="classifier-section" id="clasificador">
        <div className="classifier-intro">
          <span className="eyebrow">CLASIFICADOR VISUAL</span>
          <h2>¿Tienes un residuo a la mano?</h2>
          <p>
            Activa la cámara de tu dispositivo, muestra el objeto y EcoSorter lo
            enviará al backend para detectarlo y sugerir el contenedor correcto.
          </p>

          <div className="privacy-note">
            <span>🔒</span>
            <p>
              Tus imágenes se procesan únicamente para clasificar el residuo y no
              se almacenan permanentemente.
            </p>
          </div>
        </div>

        <WasteClassifier />
      </section>

      <section className="impact-section" id="impacto">
        <div>
          <span className="eyebrow">PEQUEÑAS ACCIONES, GRAN IMPACTO</span>
          <h2>Separar bien hoy ayuda a construir un mañana más limpio.</h2>
        </div>

        <a className="light-button" href="#clasificador">
          Empezar ahora
        </a>
      </section>

      <footer className="footer">
       <a className="brand footer-brand" href="#inicio">
  <Image
    className="brand-logo footer-logo"
    src="/ecosorter-logo.png"
    alt="Logo EcoSorter"
    width={42}
    height={42}
  />
  <span>EcoSorter</span>
</a>

        <p>Proyecto Integrador II · Universidad del Valle · 2026</p>

        <p>Clasifica, aprende y recicla mejor.</p>
      </footer>
    </main>
  );
}