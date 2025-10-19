import React from 'react';
import {
  ThreadListItemPrimitive,
  ThreadListPrimitive,
} from '@assistant-ui/react';
import { ArchiveIcon, PlusIcon } from 'lucide-react';
import { Button } from 'antd';
import { TooltipIconButton } from './TooltipIconButton';

export const ThreadList: React.FC = () => {
  return (
    <ThreadListPrimitive.Root className="flex flex-col items-stretch gap-1.5">
      <ThreadListNew />
      <ThreadListItems />
    </ThreadListPrimitive.Root>
  );
};

const ThreadListNew: React.FC = () => {
  return (
    <ThreadListPrimitive.New asChild>
      <Button
        className="data-[active]:bg-muted hover:bg-muted flex items-center justify-start gap-1 rounded-lg px-2.5 py-2 text-start"
        type="text"
      >
        <PlusIcon />
        新建对话
      </Button>
    </ThreadListPrimitive.New>
  );
};

const ThreadListItems: React.FC = () => {
  return <ThreadListPrimitive.Items components={{ ThreadListItem }} />;
};

const ThreadListItem: React.FC = () => {
  return (
    <ThreadListItemPrimitive.Root className="data-[active]:bg-muted hover:bg-muted focus-visible:bg-muted focus-visible:ring-ring flex items-center gap-2 rounded-lg transition-all focus-visible:ring-2 focus-visible:outline-none">
      <ThreadListItemPrimitive.Trigger className="flex-grow px-3 py-2 text-start">
        <ThreadListItemTitle />
      </ThreadListItemPrimitive.Trigger>
      <ThreadListItemArchive />
    </ThreadListItemPrimitive.Root>
  );
};

const ThreadListItemTitle: React.FC = () => {
  return (
    <p className="text-sm">
      <ThreadListItemPrimitive.Title fallback="新对话" />
    </p>
  );
};

const ThreadListItemArchive: React.FC = () => {
  return (
    <ThreadListItemPrimitive.Archive asChild>
      <TooltipIconButton
        className="hover:text-primary text-foreground mr-3 ml-auto size-4 p-0"
        variant="text"
        tooltip="归档对话"
      >
        <ArchiveIcon />
      </TooltipIconButton>
    </ThreadListItemPrimitive.Archive>
  );
};
