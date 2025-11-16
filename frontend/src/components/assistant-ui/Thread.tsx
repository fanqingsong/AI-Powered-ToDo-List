import React, { useEffect, useState } from 'react';
import {
  ActionBarPrimitive,
  BranchPickerPrimitive,
  ComposerPrimitive,
  MessagePrimitive,
  ThreadPrimitive,
  useAssistantState,
  ToolCallPrimitive,
} from '@assistant-ui/react';
import {
  ArrowDownIcon,
  CheckIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CopyIcon,
  PencilIcon,
  RefreshCwIcon,
  SendHorizontalIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  WrenchIcon,
} from 'lucide-react';
import { Button, Collapse, Tag, Spin } from 'antd';
import { MarkdownText } from './MarkdownText';
import { TooltipIconButton } from './TooltipIconButton';

interface ThreadProps {
  onPageNavigate?: (pageKey: string) => void;
}

export const Thread: React.FC<ThreadProps> = ({ onPageNavigate }) => {
  const state = useAssistantState();
  const messages = (state as any)?.messages || [];

  // 监听消息中的页面跳转指令
  useEffect(() => {
    const lastMessage = messages[messages.length - 1];
    if (lastMessage?.role === 'assistant' && lastMessage.content) {
      const content = lastMessage.content;
      
      // 检查是否包含页面跳转指令
      if (content.includes('navigate_to_settings') || content.includes('打开系统设置')) {
        onPageNavigate?.('settings');
      } else if (content.includes('navigate_to_tasks') || content.includes('打开任务管理')) {
        onPageNavigate?.('tasks');
      } else if (content.includes('navigate_to_calendar') || content.includes('打开日程安排')) {
        onPageNavigate?.('calendar');
      } else if (content.includes('navigate_to_notes') || content.includes('打开笔记管理')) {
        onPageNavigate?.('notes');
      } else if (content.includes('navigate_to_analytics') || content.includes('打开数据分析')) {
        onPageNavigate?.('analytics');
      }
    }
  }, [messages, onPageNavigate]);

  return (
    <ThreadPrimitive.Root
      className="flex h-full flex-col overflow-hidden"
      style={{
        ['--thread-max-width' as string]: '42rem',
      }}
    >
      <ThreadPrimitive.Viewport className="flex h-full flex-col items-center overflow-y-scroll scroll-smooth bg-inherit px-4 pt-8">
        <ThreadWelcome />

        <ThreadPrimitive.Messages
          components={{
            UserMessage: UserMessage,
            EditComposer: EditComposer,
            AssistantMessage: AssistantMessage,
          }}
        />

        <ThreadPrimitive.If empty={false}>
          <div className="min-h-8 flex-grow" />
        </ThreadPrimitive.If>

        <div className="sticky bottom-0 mt-3 flex w-full max-w-[var(--thread-max-width)] flex-col items-center justify-end rounded-t-lg bg-inherit pb-4">
          <ThreadScrollToBottom />
          <Composer />
        </div>
      </ThreadPrimitive.Viewport>
    </ThreadPrimitive.Root>
  );
};

const ThreadScrollToBottom: React.FC = () => {
  return (
    <ThreadPrimitive.ScrollToBottom asChild>
      <TooltipIconButton
        tooltip="滚动到底部"
        variant="outlined"
        className="absolute -top-8 rounded-full disabled:invisible"
      >
        <ArrowDownIcon />
      </TooltipIconButton>
    </ThreadPrimitive.ScrollToBottom>
  );
};

const ThreadWelcome: React.FC = () => {
  return (
    <ThreadPrimitive.Empty>
      <div className="flex w-full max-w-[var(--thread-max-width)] flex-grow flex-col">
        <div className="flex w-full flex-grow flex-col items-center justify-center">
          <p className="mt-4 font-medium">你好！我是你的 AI 助手</p>
          <p className="mt-2 text-sm text-gray-500">我可以帮你管理任务、安排日程，或者回答任何问题</p>
        </div>
        <ThreadWelcomeSuggestions />
      </div>
    </ThreadPrimitive.Empty>
  );
};

const ThreadWelcomeSuggestions: React.FC = () => {
  return (
    <div className="mt-3 flex w-full items-stretch justify-center gap-4">
      <ThreadPrimitive.Suggestion
        className="hover:bg-muted/80 flex max-w-sm grow basis-0 flex-col items-center justify-center rounded-lg border p-3 transition-colors ease-in"
        prompt="看看系统设置"
        method="replace"
        autoSend
      >
        <span className="line-clamp-2 text-sm font-semibold text-ellipsis">
          看看系统设置
        </span>
      </ThreadPrimitive.Suggestion>
      <ThreadPrimitive.Suggestion
        className="hover:bg-muted/80 flex max-w-sm grow basis-0 flex-col items-center justify-center rounded-lg border p-3 transition-colors ease-in"
        prompt="帮我创建一个新任务"
        method="replace"
        autoSend
      >
        <span className="line-clamp-2 text-sm font-semibold text-ellipsis">
          帮我创建一个新任务
        </span>
      </ThreadPrimitive.Suggestion>
    </div>
  );
};

const Composer: React.FC = () => {
  return (
    <ComposerPrimitive.Root className="focus-within:border-ring/20 flex w-full flex-wrap items-end rounded-lg border bg-inherit px-2.5 shadow-sm transition-colors ease-in">
      <ComposerPrimitive.Input
        rows={1}
        autoFocus
        placeholder="输入消息..."
        className="placeholder:text-muted-foreground max-h-40 flex-grow resize-none border-none bg-transparent px-2 py-4 text-sm outline-none focus:ring-0 disabled:cursor-not-allowed"
      />
      <ComposerAction />
    </ComposerPrimitive.Root>
  );
};

const ComposerAction: React.FC = () => {
  return (
    <>
      <ThreadPrimitive.If running={false}>
        <ComposerPrimitive.Send asChild>
          <TooltipIconButton
            tooltip="发送"
            variant="filled"
            className="my-2.5 size-8 p-2 transition-opacity ease-in"
          >
            <SendHorizontalIcon />
          </TooltipIconButton>
        </ComposerPrimitive.Send>
      </ThreadPrimitive.If>
      <ThreadPrimitive.If running>
        <ComposerPrimitive.Cancel asChild>
          <TooltipIconButton
            tooltip="取消"
            variant="filled"
            className="my-2.5 size-8 p-2 transition-opacity ease-in"
          >
            <CircleStopIcon />
          </TooltipIconButton>
        </ComposerPrimitive.Cancel>
      </ThreadPrimitive.If>
    </>
  );
};

const UserMessage: React.FC = () => {
  return (
    <MessagePrimitive.Root className="grid w-full max-w-[var(--thread-max-width)] auto-rows-auto grid-cols-[minmax(72px,1fr)_auto] gap-y-2 py-4 [&:where(>*)]:col-start-2">
      <UserActionBar />

      <div className="bg-muted text-foreground col-start-2 row-start-2 max-w-[calc(var(--thread-max-width)*0.8)] rounded-3xl px-5 py-2.5 break-words">
        <MessagePrimitive.Parts />
      </div>

      <BranchPicker className="col-span-full col-start-1 row-start-3 -mr-1 justify-end" />
    </MessagePrimitive.Root>
  );
};

const UserActionBar: React.FC = () => {
  return (
    <ActionBarPrimitive.Root
      hideWhenRunning
      autohide="not-last"
      className="col-start-1 row-start-2 mt-2.5 mr-3 flex flex-col items-end"
    >
      <ActionBarPrimitive.Edit asChild>
        <TooltipIconButton tooltip="编辑">
          <PencilIcon />
        </TooltipIconButton>
      </ActionBarPrimitive.Edit>
    </ActionBarPrimitive.Root>
  );
};

const EditComposer: React.FC = () => {
  return (
    <ComposerPrimitive.Root className="bg-muted my-4 flex w-full max-w-[var(--thread-max-width)] flex-col gap-2 rounded-xl">
      <ComposerPrimitive.Input className="text-foreground flex h-8 w-full resize-none bg-transparent p-4 pb-0 outline-none" />

      <div className="mx-3 mb-3 flex items-center justify-center gap-2 self-end">
        <ComposerPrimitive.Cancel asChild>
          <Button>取消</Button>
        </ComposerPrimitive.Cancel>
        <ComposerPrimitive.Send asChild>
          <Button type="primary">发送</Button>
        </ComposerPrimitive.Send>
      </div>
    </ComposerPrimitive.Root>
  );
};

// 工具调用显示组件
const ToolCallDisplay: React.FC<{ toolName: string; toolCallId: string }> = ({ toolName, toolCallId }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <ToolCallPrimitive.Root toolCallId={toolCallId}>
      <div className="mb-3 rounded-lg border border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800">
        <div
          className="flex cursor-pointer items-center justify-between p-3 transition-colors hover:bg-gray-100 dark:hover:bg-gray-700"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center gap-2">
            <WrenchIcon className="h-4 w-4 text-gray-500" />
            <span className="font-medium text-sm">{toolName}</span>
            <ToolCallPrimitive.If status="result">
              <Tag color="success" className="text-xs">完成</Tag>
            </ToolCallPrimitive.If>
            <ToolCallPrimitive.If status="error">
              <Tag color="error" className="text-xs">错误</Tag>
            </ToolCallPrimitive.If>
            <ToolCallPrimitive.If status="partial-call">
              <Tag color="processing" className="text-xs">执行中</Tag>
            </ToolCallPrimitive.If>
          </div>
          {isExpanded ? (
            <ChevronUpIcon className="h-4 w-4 text-gray-500" />
          ) : (
            <ChevronDownIcon className="h-4 w-4 text-gray-500" />
          )}
        </div>
        {isExpanded && (
          <div className="border-t border-gray-200 p-3 dark:border-gray-700">
            <ToolCallPrimitive.If hasArgs>
              <div className="mb-2">
                <div className="mb-1 text-xs font-medium text-gray-600 dark:text-gray-400">
                  参数:
                </div>
                <pre className="max-h-32 overflow-auto rounded bg-white p-2 text-xs dark:bg-gray-900">
                  <ToolCallPrimitive.Args />
                </pre>
              </div>
            </ToolCallPrimitive.If>
            <ToolCallPrimitive.If status="result">
              <div>
                <div className="mb-1 text-xs font-medium text-gray-600 dark:text-gray-400">
                  结果:
                </div>
                <pre className="max-h-32 overflow-auto rounded bg-white p-2 text-xs dark:bg-gray-900">
                  <ToolCallPrimitive.Result />
                </pre>
              </div>
            </ToolCallPrimitive.If>
            <ToolCallPrimitive.If status="error">
              <div className="text-xs text-red-600 dark:text-red-400">
                工具调用出错
              </div>
            </ToolCallPrimitive.If>
            <ToolCallPrimitive.If status="partial-call">
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <Spin size="small" />
                <span>正在执行...</span>
              </div>
            </ToolCallPrimitive.If>
          </div>
        )}
      </div>
    </ToolCallPrimitive.Root>
  );
};

// 工具调用组容器
const ToolCallGroup: React.FC<{ startIndex: number; endIndex: number; children: React.ReactNode }> = ({
  children,
}) => {
  return (
    <div className="mb-4 rounded-lg border border-blue-200 bg-blue-50 p-3 dark:border-blue-800 dark:bg-blue-900/20">
      <div className="mb-2 flex items-center gap-2">
        <WrenchIcon className="h-4 w-4 text-blue-600 dark:text-blue-400" />
        <span className="text-sm font-medium text-blue-900 dark:text-blue-100">
          工具调用
        </span>
      </div>
      <div className="space-y-2">{children}</div>
    </div>
  );
};

// 单个工具调用组件（用于 MessagePrimitive.Parts 的 tools 配置）
const ToolCallComponent: React.FC<{ toolCallId: string; toolName: string }> = ({
  toolCallId,
  toolName,
}) => {
  return <ToolCallDisplay toolName={toolName} toolCallId={toolCallId} />;
};

const AssistantMessage: React.FC = () => {
  return (
    <MessagePrimitive.Root className="relative grid w-full max-w-[var(--thread-max-width)] grid-cols-[auto_auto_1fr] grid-rows-[auto_1fr] py-4">
      <div className="text-foreground col-span-2 col-start-2 row-start-1 my-1.5 max-w-[calc(var(--thread-max-width)*0.8)] leading-7 break-words">
        <MessagePrimitive.Parts
          components={{
            Text: MarkdownText,
            ToolGroup: ToolCallGroup,
            tools: {
              Fallback: ({ toolCallId, toolName }: { toolCallId: string; toolName: string }) => (
                <ToolCallComponent toolCallId={toolCallId} toolName={toolName} />
              ),
            },
          }}
        />
      </div>

      <AssistantActionBar />

      <BranchPicker className="col-start-2 row-start-2 mr-2 -ml-2" />
    </MessagePrimitive.Root>
  );
};

const AssistantActionBar: React.FC = () => {
  return (
    <ActionBarPrimitive.Root
      hideWhenRunning
      autohide="not-last"
      autohideFloat="single-branch"
      className="text-muted-foreground data-[floating]:bg-background col-start-3 row-start-2 -ml-1 flex gap-1 data-[floating]:absolute data-[floating]:rounded-md data-[floating]:border data-[floating]:p-1 data-[floating]:shadow-sm"
    >
      <ActionBarPrimitive.Copy asChild>
        <TooltipIconButton tooltip="复制">
          <MessagePrimitive.If copied>
            <CheckIcon />
          </MessagePrimitive.If>
          <MessagePrimitive.If copied={false}>
            <CopyIcon />
          </MessagePrimitive.If>
        </TooltipIconButton>
      </ActionBarPrimitive.Copy>
      <ActionBarPrimitive.Reload asChild>
        <TooltipIconButton tooltip="刷新">
          <RefreshCwIcon />
        </TooltipIconButton>
      </ActionBarPrimitive.Reload>
    </ActionBarPrimitive.Root>
  );
};

const BranchPicker: React.FC<BranchPickerPrimitive.Root.Props> = ({
  className,
  ...rest
}) => {
  return (
    <BranchPickerPrimitive.Root
      hideWhenSingleBranch
      className={`text-muted-foreground inline-flex items-center text-xs ${className || ''}`}
      {...rest}
    >
      <BranchPickerPrimitive.Previous asChild>
        <TooltipIconButton tooltip="上一个">
          <ChevronLeftIcon />
        </TooltipIconButton>
      </BranchPickerPrimitive.Previous>
      <span className="font-medium">
        <BranchPickerPrimitive.Number /> / <BranchPickerPrimitive.Count />
      </span>
      <BranchPickerPrimitive.Next asChild>
        <TooltipIconButton tooltip="下一个">
          <ChevronRightIcon />
        </TooltipIconButton>
      </BranchPickerPrimitive.Next>
    </BranchPickerPrimitive.Root>
  );
};

const CircleStopIcon = () => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 16 16"
      fill="currentColor"
      width="16"
      height="16"
    >
      <rect width="10" height="10" x="3" y="3" rx="2" />
    </svg>
  );
};
