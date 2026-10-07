/**
 * OGGY X — Pure Fullscreen Live AI Voice Assistant Frontend Controller
 * Ensures 100% character and background consistency across all states.
 */

// Consistent Video Sources (Same character model, framing, and cyan background)
const VIDEO_PATHS = {
  idle: "/static/videos/idle_consistent.mp4",
  idle_wiggle: "/static/videos/idle_wiggle.mp4",
  listening: "/static/videos/listening_consistent.mp4",
  thinking: "/static/videos/thinking_consistent.mp4",
  speaking: "/static/videos/speaking_consistent.mp4",
  speaking_expressive: "/static/videos/speaking_expressive.mp4"
};

// DOM Elements
const videoPrimary = document.getElementById("video-primary");
const videoSecondary = document.getElementById("video-secondary");
const videoWrapper = document.getElementById("video-wrapper");
const characterStage = document.getElementById("character-stage");
const statePill = document.getElementById("state-pill");
const stateText = document.getElementById("state-text");
const btnMic = document.getElementById("btn-mic");
const textInput = document.getElementById("text-input");
const btnSend = document.getElementById("btn-send");
const btnSettings = document.getElementById("btn-settings");
const settingsModal = document.getElementById("settings-modal");
const btnCloseModal = document.getElementById("btn-close-modal");
const btnSaveKey = document.getElementById("btn-save-key");
const btnClearKey = document.getElementById("btn-clear-key");
const geminiKeyInput = document.getElementById("gemini-key-input");
const keyStatusText = document.getElementById("key-status-text");

const wakeIndicator = document.getElementById("wake-indicator");
const wakeText = document.getElementById("wake-text");
const btnPip = document.getElementById("btn-pip");
const pipCanvas = document.getElementById("pip-canvas");
const pipVideo = document.getElementById("pip-video");

// Application State
let currentState = "idle";
let activeVideo = videoPrimary;
let inactiveVideo = videoSecondary;
let recognition = null;
let currentAudio = null;
let idleEmotionTimer = null;

// Wake Word & Recognition State
let wakeWordActive = true;
let speechRecognizerRunning = false;
const WAKE_WORD_REGEX = /\b(listen\s+oggy|listen\s+ogy|listening\s+oggy|listen\s+augy|hey\s+oggy|hi\s+oggy|hello\s+oggy|ok\s+oggy|oggy)\b/i;

// Picture-in-Picture State
let pipActive = false;
let pipAnimId = null;
let pipCtx = null;
let pipDocumentWindow = null;

// Parallax tracking
let mouseX = window.innerWidth / 2;
let mouseY = window.innerHeight / 2;
let rotY = 0;
let rotX = 0;
let transX = 0;
let transY = 0;

// ================= 1. VIDEO SEAMLESS CROSSFADER =================
function initVideos() {
  // Start silently in consistent calm idle
  videoPrimary.src = VIDEO_PATHS.idle;
  videoPrimary.loop = true;
  videoPrimary.play().catch(e => console.log("Waiting for user interaction:", e));
  scheduleIdleEmotion();
}

function switchVideo(videoKey, loop = true) {
  const targetSrc = VIDEO_PATHS[videoKey] || VIDEO_PATHS.idle;

  // Avoid redundant reload if same video is already active
  if (activeVideo.src.endsWith(targetSrc) && !activeVideo.paused) {
    activeVideo.loop = loop;
    return;
  }

  inactiveVideo.src = targetSrc;
  inactiveVideo.loop = loop;

  inactiveVideo.play().then(() => {
    inactiveVideo.classList.remove("inactive");
    inactiveVideo.classList.add("active");

    activeVideo.classList.remove("active");
    activeVideo.classList.add("inactive");

    setTimeout(() => {
      activeVideo.pause();
      const tmp = activeVideo;
      activeVideo = inactiveVideo;
      inactiveVideo = tmp;
    }, 220);
  }).catch(e => console.warn("Video play error:", e));
}

// ================= 2. IDLE FUNNY EMOTIONS (COMPLETELY SILENT) =================
function scheduleIdleEmotion() {
  clearTimeout(idleEmotionTimer);
  // Trigger a silent, funny ear-wiggle emotion every 18-24 seconds while idle
  const delay = Math.random() * 6000 + 18000;
  idleEmotionTimer = setTimeout(() => {
    if (currentState === "idle") {
      playIdleWiggle();
    }
  }, delay);
}

function playIdleWiggle() {
  if (currentState !== "idle") return;
  // Briefly play funny wiggle without any speech
  switchVideo("idle_wiggle", false);
  
  // Return to calm idle after wiggle duration (2.5s)
  setTimeout(() => {
    if (currentState === "idle") {
      switchVideo("idle", true);
      scheduleIdleEmotion();
    }
  }, 2500);
}

// ================= 3. STATE CONTROLLER =================
function setState(newState, meta = {}) {
  // If moving away from speaking, immediately stop any ongoing speech audio
  if (currentState === "speaking" && newState !== "speaking") {
    stopCurrentSpeech();
  }

  currentState = newState;
  clearTimeout(idleEmotionTimer);

  switch (newState) {
    case "idle":
      statePill.classList.add("hidden");
      statePill.style.cursor = "default";
      statePill.title = "";
      statePill.onclick = null;
      btnMic.classList.remove("listening");
      switchVideo("idle", true);
      scheduleIdleEmotion();
      updateWakeUI();
      // Ensure wake word recognition is running in idle
      if (wakeWordActive && !speechRecognizerRunning) {
        setTimeout(startSpeechRecognition, 350);
      }
      break;

    case "listening":
      statePill.classList.remove("hidden");
      statePill.style.cursor = "default";
      statePill.title = "";
      statePill.onclick = null;
      stateText.textContent = "Listening to you, Naveen...";
      btnMic.classList.add("listening");
      switchVideo("listening", true);
      updateWakeUI();
      if (!speechRecognizerRunning) {
        startSpeechRecognition();
      }
      break;

    case "thinking":
      statePill.classList.remove("hidden");
      statePill.style.cursor = "default";
      statePill.title = "";
      statePill.onclick = null;
      stateText.textContent = "Oggy thinking...";
      btnMic.classList.remove("listening");
      switchVideo("thinking", false);
      updateWakeUI();
      break;

    case "speaking":
      statePill.classList.remove("hidden");
      updateWakeUI();
      
      // If an action is triggered, indicate what is opening
      if (meta.action && meta.action.type === "open_url" && meta.action.url) {
        const actionUrl = meta.action.url;
        stateText.textContent = `Opening ${meta.action.title || "app"}...`;
        statePill.style.cursor = "pointer";
        statePill.title = `Click to open ${meta.action.title || actionUrl}`;
        statePill.onclick = () => {
          window.open(actionUrl, "_blank");
        };

        // Open automatically after 900ms so Oggy visibly speaks first
        setTimeout(() => {
          try {
            window.open(actionUrl, "_blank");
          } catch (err) {
            console.warn("[Action] Auto-open failed:", err);
          }
        }, 900);
      } else {
        stateText.textContent = "Oggy speaking! (Tap to stop)";
        statePill.style.cursor = "pointer";
        statePill.title = "Tap to interrupt speech";
        statePill.onclick = () => {
          stopCurrentSpeech();
          setState("idle");
        };
      }
      btnMic.classList.remove("listening");

      // Pick consistent speaking clip
      const style = Math.random() > 0.4 ? "speaking" : "speaking_expressive";
      switchVideo(style, true);

      // Play neural speech audio
      playVoice(meta.audio_url, meta.answer, () => {
        // Return seamlessly to calm idle as soon as speech finishes
        setTimeout(() => {
          if (currentState === "speaking") {
            setState("idle");
          }
        }, 350);
      });
      break;
  }
}

// ================= 4. BULLETPROOF HYBRID VOICE PLAYBACK WITH INTERRUPTION =================
let currentSpeechController = null;

function stopCurrentSpeech() {
  if (currentSpeechController) {
    try {
      currentSpeechController.abort();
    } catch (e) {}
    currentSpeechController = null;
  }
  if (currentAudio) {
    try {
      currentAudio.onended = null;
      currentAudio.onerror = null;
      currentAudio.onplaying = null;
      currentAudio.pause();
      currentAudio.src = "";
    } catch (e) {}
    currentAudio = null;
  }
  if ("speechSynthesis" in window) {
    try {
      window.speechSynthesis.cancel();
    } catch (e) {}
  }
}

function playVoice(audioUrl, text, onComplete) {
  stopCurrentSpeech();

  let finished = false;
  let activeAudio = null;

  const markDone = (wasInterrupted = false) => {
    if (finished) return;
    finished = true;
    currentSpeechController = null;
    if (activeAudio) {
      activeAudio.onended = null;
      activeAudio.onerror = null;
      activeAudio.onplaying = null;
      try { activeAudio.pause(); } catch(e){}
      activeAudio = null;
    }
    if ("speechSynthesis" in window) {
      try { window.speechSynthesis.cancel(); } catch(e){}
    }
    currentAudio = null;
    if (!wasInterrupted && onComplete) onComplete();
  };

  currentSpeechController = {
    abort: () => markDone(true)
  };

  // Fallback function: Uses speech synthesis with natural duration protection
  const startLocalSpeech = () => {
    if (finished) return;
    console.log("[Voice] Using local browser speech synthesis");

    if (!("speechSynthesis" in window) || !text) {
      markDone();
      return;
    }

    const utt = new SpeechSynthesisUtterance(text);
    utt.pitch = 1.35; // Cartoon cat pitch
    utt.rate = 1.05;  // Lively pace

    const voices = window.speechSynthesis.getVoices();
    const best = voices.find(v => v.lang.startsWith("en") && (v.name.includes("Google") || v.name.includes("Natural") || v.name.includes("Samantha") || v.name.includes("English")));
    if (best) utt.voice = best;

    // Minimum reading time based on word count (approx 280ms per word, min 2.0s)
    const wordCount = (text || "").split(/\s+/).length;
    const expectedDurationMs = Math.max(2000, wordCount * 280);
    const startTime = Date.now();

    utt.onend = () => {
      const elapsed = Date.now() - startTime;
      if (elapsed < 200) {
        // If onend fired instantly (common browser quirk), keep speaking animation for natural duration
        setTimeout(markDone, expectedDurationMs);
      } else {
        markDone();
      }
    };

    utt.onerror = (e) => {
      console.warn("[Voice] Local speech error, sustaining animation:", e);
      setTimeout(markDone, expectedDurationMs);
    };

    window.speechSynthesis.speak(utt);
  };

  // Primary: Try Neural Audio if URL is available
  if (audioUrl) {
    const audio = new Audio();
    activeAudio = audio;
    currentAudio = audio;
    let audioStarted = false;

    // 2.5s Watchdog: If audio doesn't start, gracefully switch to local speech
    const timer = setTimeout(() => {
      if (!audioStarted && !finished) {
        console.warn("[Voice] Audio load timeout, falling back to local speech");
        if (activeAudio) {
          activeAudio.onplaying = null;
          activeAudio.onended = null;
          activeAudio.onerror = null;
          try { activeAudio.pause(); } catch(e){}
          activeAudio.src = "";
          activeAudio = null;
        }
        startLocalSpeech();
      }
    }, 2500);

    audio.onplaying = () => {
      audioStarted = true;
      clearTimeout(timer);
    };

    audio.onended = () => {
      clearTimeout(timer);
      markDone();
    };

    audio.onerror = () => {
      clearTimeout(timer);
      if (!finished && !audioStarted) {
        console.warn("[Voice] Audio file error, falling back to local speech");
        if (activeAudio) {
          activeAudio.onplaying = null;
          activeAudio.onended = null;
          activeAudio.onerror = null;
          try { activeAudio.pause(); } catch(e){}
          activeAudio.src = "";
          activeAudio = null;
        }
        startLocalSpeech();
      }
    };

    audio.src = audioUrl;
    audio.play().catch(err => {
      clearTimeout(timer);
      if (!finished && !audioStarted) {
        console.warn("[Voice] play() rejected:", err.message);
        if (activeAudio) {
          activeAudio.onplaying = null;
          activeAudio.onended = null;
          activeAudio.onerror = null;
          try { activeAudio.pause(); } catch(e){}
          activeAudio.src = "";
          activeAudio = null;
        }
        startLocalSpeech();
      }
    });
  } else {
    startLocalSpeech();
  }
}

// ================= 5. 3D MOUSE PARALLAX =================
window.addEventListener("mousemove", (e) => {
  mouseX = e.clientX;
  mouseY = e.clientY;
});

function animateParallax() {
  const cx = window.innerWidth / 2;
  const cy = window.innerHeight / 2;

  const nx = (mouseX - cx) / cx;
  const ny = (mouseY - cy) / cy;

  const targetRotY = nx * 7;
  const targetRotX = -ny * 4;
  const targetTransX = nx * 12;
  const targetTransY = ny * 8;

  rotY += (targetRotY - rotY) * 0.08;
  rotX += (targetRotX - rotX) * 0.08;
  transX += (targetTransX - transX) * 0.08;
  transY += (targetTransY - transY) * 0.08;

  if (videoWrapper) {
    videoWrapper.style.transform = `rotateY(${rotY}deg) rotateX(${rotX}deg) translate3d(${transX}px, ${transY}px, 0)`;
  }

  requestAnimationFrame(animateParallax);
}

// ================= 6. ASYNC QUERY RESOLUTION =================
async function askOggy(query) {
  if (!query || !query.trim()) return;

  // Interrupt and cancel any previous speech
  stopCurrentSpeech();
  setState("thinking");

  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query.trim() })
    });

    if (res.ok) {
      const data = await res.json();
      setState("speaking", data);
    } else {
      setState("speaking", {
        answer: "Meow! Joey scrambled my wires! Try asking me again!",
        audio_url: ""
      });
    }
  } catch (err) {
    console.error("Ask API error:", err);
    setState("speaking", {
      answer: "Oops! Looks like the cockroaches cut the wifi! Please check your connection!",
      audio_url: ""
    });
  }
}

// ================= 7. WAKE WORD & SPEECH RECOGNITION =================
function updateWakeUI() {
  if (!wakeIndicator) return;
  if (!wakeWordActive) {
    wakeIndicator.classList.add("disabled");
    wakeIndicator.classList.remove("listening");
    wakeText.textContent = "Wake: Off";
  } else if (currentState === "listening") {
    wakeIndicator.classList.remove("disabled");
    wakeIndicator.classList.add("listening");
    wakeText.textContent = "Listening to you...";
  } else {
    wakeIndicator.classList.remove("disabled", "listening");
    wakeText.textContent = 'Wake: "Listen Oggy"';
  }
}

function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    if (wakeIndicator) {
      wakeIndicator.classList.add("disabled");
      wakeText.textContent = "Speech API Unavailable";
    }
    return;
  }

  recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = "en-US";

  recognition.onstart = () => {
    speechRecognizerRunning = true;
    updateWakeUI();
  };

  recognition.onresult = (e) => {
    // If currently SPEAKING: Allow barge-in / interrupt commands ("Stop", "Listen Oggy", etc.)
    if (currentState === "speaking") {
      const matchStop = currentText.match(/\b(stop|stop talking|be quiet|shut up|pause|cancel)\b/i);
      const matchWake = currentText.match(WAKE_WORD_REGEX);

      if (matchStop) {
        console.log("[BargeIn] User commanded stop while speaking");
        stopCurrentSpeech();
        setState("idle");
        return;
      }

      if (matchWake) {
        console.log("[BargeIn] User said wake word while speaking");
        stopCurrentSpeech();
        const wakePhrase = matchWake[0];
        const remainder = currentText.substring(currentText.indexOf(wakePhrase) + wakePhrase.length)
                                     .replace(/^[,\s.!?:;]+/, "").trim();
        if (remainder.length >= 3) {
          textInput.value = remainder;
          askOggy(remainder);
        } else {
          setState("listening");
        }
        return;
      }
      return;
    }

    let interimTranscript = "";
    let finalTranscript = "";

    for (let i = e.resultIndex; i < e.results.length; ++i) {
      const trans = e.results[i][0].transcript;
      if (e.results[i].isFinal) {
        finalTranscript += trans;
      } else {
        interimTranscript += trans;
      }
    }

    const currentText = (finalTranscript || interimTranscript).trim().toLowerCase();
    if (!currentText) return;

    // 1. If currently in IDLE: Check for wake word "Listen Oggy"
    if (currentState === "idle") {
      const match = currentText.match(WAKE_WORD_REGEX);
      if (match) {
        const wakePhrase = match[0];
        const remainder = currentText.substring(currentText.indexOf(wakePhrase) + wakePhrase.length)
                                     .replace(/^[,\s.!?:;]+/, "").trim();

        if (remainder.length >= 3) {
          // Direct command said with wake word: "Listen Oggy, what time is it?"
          console.log("[WakeWord] Direct query recognized:", remainder);
          textInput.value = remainder;
          askOggy(remainder);
        } else {
          // Just wake word: "Listen Oggy"
          console.log("[WakeWord] Keyword activated! Entering listening state");
          setState("listening");
        }
      }
    }
    // 2. If currently in LISTENING: Capture user question
    else if (currentState === "listening") {
      if (finalTranscript && finalTranscript.trim().length > 1) {
        // Strip duplicate wake word prefix if spoken again
        const cleanQuery = finalTranscript.replace(WAKE_WORD_REGEX, "")
                                          .replace(/^[,\s.!?:;]+/, "")
                                          .trim() || finalTranscript.trim();
        if (cleanQuery.length >= 2) {
          console.log("[Voice] Captured user query:", cleanQuery);
          textInput.value = cleanQuery;
          askOggy(cleanQuery);
        }
      }
    }
  };

  recognition.onerror = (e) => {
    if (e.error !== "no-speech" && e.error !== "aborted") {
      console.warn("Speech recognition notice:", e.error);
    }
  };

  recognition.onend = () => {
    speechRecognizerRunning = false;
    updateWakeUI();
    // Auto-restart if wake-word is active
    if (wakeWordActive) {
      setTimeout(() => {
        startSpeechRecognition();
      }, 350);
    }
  };

  startSpeechRecognition();
}

function startSpeechRecognition() {
  if (!recognition || speechRecognizerRunning) return;
  try {
    recognition.start();
  } catch (err) {
    // Requires initial user interaction on standard web browsers
  }
}

function toggleMic() {
  // Prime video & audio on user click
  if (videoPrimary.paused) {
    videoPrimary.play().catch(() => {});
  }

  if (!recognition) {
    alert("Microphone recognition is supported in Chrome, Chromium, and Brave. You can also type directly in the box below!");
    return;
  }

  if (currentState === "speaking") {
    // User clicked mic while Oggy was speaking: interrupt immediately and listen!
    stopCurrentSpeech();
    startSpeechRecognition();
    setState("listening");
  } else if (currentState === "listening") {
    setState("idle");
  } else {
    startSpeechRecognition();
    setState("listening");
  }
}

function toggleWakeWord() {
  wakeWordActive = !wakeWordActive;
  if (wakeWordActive) {
    startSpeechRecognition();
  } else {
    if (speechRecognizerRunning && recognition) {
      try { recognition.stop(); } catch(e){}
    }
  }
  updateWakeUI();
}

// ================= 8. PICTURE-IN-PICTURE (PiP) ENGINE =================
function initPiP() {
  if (!pipCanvas || !pipVideo) return;
  pipCtx = pipCanvas.getContext("2d");

  // Continuous render loop mirroring active character video to canvas
  function renderPiPFrame() {
    if (pipActive && pipCtx && activeVideo) {
      try {
        if (activeVideo.readyState >= 2) {
          pipCtx.drawImage(activeVideo, 0, 0, pipCanvas.width, pipCanvas.height);
        }
      } catch (e) {}
    }
    pipAnimId = requestAnimationFrame(renderPiPFrame);
  }
  pipAnimId = requestAnimationFrame(renderPiPFrame);

  pipVideo.addEventListener("leavepictureinpicture", () => {
    pipActive = false;
    if (btnPip) btnPip.classList.remove("active");
  });
}

async function togglePiP() {
  if (document.pictureInPictureElement || pipDocumentWindow || pipActive) {
    exitPiP();
    return;
  }

  // 1. Document Picture-in-Picture API (Chromium / Chrome / Brave)
  if ("documentPictureInPicture" in window) {
    try {
      pipDocumentWindow = await window.documentPictureInPicture.requestWindow({
        width: 360,
        height: 430
      });

      const pipDoc = pipDocumentWindow.document;
      pipDoc.title = "OGGY X Floating Assistant";

      // Replicate styles
      document.querySelectorAll('link[rel="stylesheet"], style').forEach((node) => {
        pipDoc.head.appendChild(node.cloneNode(true));
      });

      const container = pipDoc.createElement("div");
      container.style.cssText = "width:100vw; height:100vh; background:#2babc4; display:flex; flex-direction:column; align-items:center; justify-content:space-between; overflow:hidden; position:relative; font-family:'Fredoka',sans-serif;";

      const pipVid = pipDoc.createElement("video");
      pipVid.autoplay = true;
      pipVid.playsInline = true;
      pipVid.muted = true;
      pipVid.loop = true;
      pipVid.style.cssText = "width:100%; height:82%; object-fit:contain; background:#2babc4;";
      pipVid.src = activeVideo.src;
      pipVid.currentTime = activeVideo.currentTime;
      pipVid.play().catch(() => {});

      // Synchronize video when state changes
      const syncInterval = setInterval(() => {
        if (!pipDocumentWindow || pipDocumentWindow.closed) {
          clearInterval(syncInterval);
          return;
        }
        if (activeVideo.src && !pipVid.src.endsWith(activeVideo.src.split("/").pop())) {
          pipVid.src = activeVideo.src;
          pipVid.currentTime = activeVideo.currentTime;
          pipVid.play().catch(() => {});
        }
      }, 200);

      const bottomBar = pipDoc.createElement("div");
      bottomBar.style.cssText = "height:18%; width:100%; display:flex; align-items:center; justify-content:center; gap:10px; background:rgba(14,38,55,0.75); backdrop-filter:blur(12px);";

      const statusSpan = pipDoc.createElement("span");
      statusSpan.style.cssText = "color:#ffffff; font-size:12px; font-weight:600; text-transform:uppercase;";
      statusSpan.textContent = "OGGY X Active";

      const miniMic = pipDoc.createElement("button");
      miniMic.textContent = "🎙️ Speak";
      miniMic.style.cssText = "background:linear-gradient(135deg, #00f2fe, #4facfe); color:#0b2d42; border:none; padding:6px 14px; border-radius:20px; font-weight:700; cursor:pointer; font-size:12px;";
      miniMic.onclick = () => {
        toggleMic();
      };

      bottomBar.appendChild(statusSpan);
      bottomBar.appendChild(miniMic);
      container.appendChild(pipVid);
      container.appendChild(bottomBar);
      pipDoc.body.style.margin = "0";
      pipDoc.body.appendChild(container);

      pipDocumentWindow.addEventListener("pagehide", () => {
        pipDocumentWindow = null;
        pipActive = false;
        if (btnPip) btnPip.classList.remove("active");
      });

      pipActive = true;
      if (btnPip) btnPip.classList.add("active");
      return;
    } catch (err) {
      console.log("Document PiP declined/unavailable, falling back to Video Canvas PiP:", err);
    }
  }

  // 2. Fallback: Universal Canvas Stream Video PiP
  try {
    pipActive = true;
    if (btnPip) btnPip.classList.add("active");

    const stream = pipCanvas.captureStream(30);
    pipVideo.srcObject = stream;
    await pipVideo.play();
    await pipVideo.requestPictureInPicture();
  } catch (err) {
    console.warn("Video PiP failed:", err);
    pipActive = false;
    if (btnPip) btnPip.classList.remove("active");
    alert("Picture-in-Picture mode ready: Tap again or permit floating window in browser.");
  }
}

function exitPiP() {
  if (document.pictureInPictureElement) {
    document.exitPictureInPicture().catch(() => {});
  }
  if (pipDocumentWindow && !pipDocumentWindow.closed) {
    pipDocumentWindow.close();
    pipDocumentWindow = null;
  }
  pipActive = false;
  if (btnPip) btnPip.classList.remove("active");
}

// ================= 8. SETTINGS MODAL =================
async function loadConfig() {
  try {
    const res = await fetch("/api/config");
    if (res.ok) {
      const data = await res.json();
      if (data.has_gemini_key) {
        keyStatusText.textContent = `Active Key: ${data.masked_key}`;
        keyStatusText.style.color = "#a3ff12";
      } else {
        keyStatusText.textContent = "No key saved (Using local feed)";
        keyStatusText.style.color = "rgba(255, 255, 255, 0.6)";
      }
    }
  } catch (e) {}
}

function setupEvents() {
  btnMic.addEventListener("click", toggleMic);
  if (btnPip) btnPip.addEventListener("click", togglePiP);
  if (wakeIndicator) wakeIndicator.addEventListener("click", toggleWakeWord);

  btnSend.addEventListener("click", () => {
    const q = textInput.value;
    textInput.value = "";
    askOggy(q);
  });

  textInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      const q = textInput.value;
      textInput.value = "";
      askOggy(q);
    }
  });

  // Interactive click on stage / Oggy character
  characterStage.addEventListener("click", (e) => {
    // Prime speech engine on first user interaction
    startSpeechRecognition();

    // Spawn touch ripple at click position
    spawnTouchRipple(e.clientX, e.clientY);

    if (currentState === "speaking") {
      // Interactive reaction while speaking: dynamically toggle expressive cartoon gesture!
      const currentSrc = activeVideo.src || "";
      const nextStyle = currentSrc.includes("speaking_expressive") ? "speaking" : "speaking_expressive";
      switchVideo(nextStyle, true);
    } else if (currentState === "idle") {
      playIdleWiggle();
    }
  });

  // Keyboard Escape key to interrupt speech or cancel listening immediately
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (currentState === "speaking" || currentState === "listening") {
        stopCurrentSpeech();
        setState("idle");
      }
    }
  });

  // Global user gesture trigger to unlock audio/mic permissions
  document.addEventListener("click", () => {
    if (!speechRecognizerRunning && wakeWordActive) {
      startSpeechRecognition();
    }
  }, { once: true });

  // Settings Modal
  btnSettings.addEventListener("click", () => {
    settingsModal.classList.remove("hidden");
  });

  btnCloseModal.addEventListener("click", () => {
    settingsModal.classList.add("hidden");
  });

  settingsModal.addEventListener("click", (e) => {
    if (e.target === settingsModal) {
      settingsModal.classList.add("hidden");
    }
  });

  btnSaveKey.addEventListener("click", async () => {
    const key = geminiKeyInput.value.trim();
    const res = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ gemini_api_key: key })
    });
    if (res.ok) {
      geminiKeyInput.value = "";
      settingsModal.classList.add("hidden");
      loadConfig();
    }
  });

  btnClearKey.addEventListener("click", async () => {
    await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ gemini_api_key: "" })
    });
    geminiKeyInput.value = "";
    loadConfig();
  });
}

function spawnTouchRipple(x, y) {
  try {
    if (!x && !y) return;
    const ripple = document.createElement("div");
    ripple.className = "touch-ripple";
    ripple.style.left = `${x}px`;
    ripple.style.top = `${y}px`;
    document.body.appendChild(ripple);
    setTimeout(() => {
      try { ripple.remove(); } catch (e) {}
    }, 700);
  } catch (e) {}
}

// ================= 9. INIT =================
window.addEventListener("DOMContentLoaded", () => {
  initVideos();
  initPiP();
  initSpeechRecognition();
  animateParallax();
  setupEvents();
  loadConfig();
});
