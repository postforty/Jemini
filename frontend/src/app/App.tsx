import { GradientDefs } from '@/shared/ui';
import { ChatPage } from '@/pages/chat';
import { AuthModal } from '@/features/auth';
import { PaymentModal } from '@/features/payment';
import { useChatStore } from '@/entities/chat';
import './styles/global.css';

export default function App() {
  const setSelectedModel = useChatStore((s) => s.setSelectedModel);

  return (
    <>
      <GradientDefs />
      <ChatPage />
      <AuthModal />
      <PaymentModal onSuccess={(chosenModel) => {
        if (chosenModel) {
          setSelectedModel(chosenModel);
        }
      }} />
    </>
  );
}

