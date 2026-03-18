import { useState, useCallback, useEffect } from 'react';

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

export const useWellnessVoice = (lang = 'en') => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);

  // Initialize Speech Recognition
  const recognition = SpeechRecognition ? new SpeechRecognition() : null;
  if (recognition) {
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = lang === 'hi' ? 'hi-IN' : 'en-IN';
  }

  const speak = useCallback((text, currentLang = lang) => {
    if (!window.speechSynthesis) return;

    window.speechSynthesis.cancel(); // Stop current speech

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Enhanced Voice Model Selection
    const voices = window.speechSynthesis.getVoices();
    const voiceLang = currentLang === 'hi' ? 'hi-IN' : 'en-IN';
    
    // Prioritize high-quality/natural voices (Google, Daniel, etc.)
    const premiumVoice = voices.find(v => (v.name.includes('Google') || v.name.includes('Natural')) && v.lang.startsWith(voiceLang.split('-')[0])) ||
                        voices.find(v => v.lang.startsWith(voiceLang.split('-')[0]));
    
    if (premiumVoice) utterance.voice = premiumVoice;
    
    utterance.lang = voiceLang;
    // Clinical Modulation: 0.9x rate = Authoritative & Calm, 1.1 pitch = Caring/Optimistic
    utterance.rate = 0.92;
    utterance.pitch = 1.05;
    utterance.volume = 1.0;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = (e) => {
        console.error('TTS Error:', e);
        setIsSpeaking(false);
    };

    window.speechSynthesis.speak(utterance);
  }, [lang]);

  const listen = useCallback(() => {
    if (!recognition) {
      console.error('Speech recognition not supported in this browser.');
      return;
    }

    setTranscript('');
    setIsListening(true);
    
    try {
      recognition.start();
    } catch (e) {
      console.error('Recognition error:', e);
      setIsListening(false);
    }

    recognition.onresult = (event) => {
      const result = event.results[0][0].transcript;
      setTranscript(result);
      setIsListening(false);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };
  }, [recognition]);

  const stopListening = useCallback(() => {
    if (recognition) {
      recognition.stop();
      setIsListening(false);
    }
  }, [recognition]);

  const stopSpeaking = useCallback(() => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  }, []);

  return {
    isListening,
    transcript,
    isSpeaking,
    speak,
    listen,
    stopListening,
    stopSpeaking,
    hasSupport: !!recognition
  };
};
