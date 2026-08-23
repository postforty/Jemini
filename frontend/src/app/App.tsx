import { GradientDefs } from '@/shared/ui';
import { ChatPage } from '@/pages/chat';
import { AuthModal } from '@/features/auth';
import './styles/global.css';

export default function App() {
  return (
    <>
      <GradientDefs />
      <ChatPage />
      <AuthModal />
    </>
  );
}
