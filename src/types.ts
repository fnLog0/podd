export interface WorkflowState {
  audioFilePath: string;
  transcribedText: string;
  messages: string[];
  aiResponse: string;
  ttsAudioPath: string;
}
