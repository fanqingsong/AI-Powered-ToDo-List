"""
笔记管理工具类
"""

from langchain_core.tools import tool
from typing import List, Any, Dict, Optional
from ....services.sync_note_service import SyncNoteService
from ....models.note import NoteCreate, NoteUpdate, NoteCategoryEnum


class NoteTools:
    """笔记管理工具类"""
    
    def __init__(self):
        self.note_service = SyncNoteService()
        self.current_user_id = None
    
    def set_user_id(self, user_id: int):
        """设置当前用户ID"""
        self.current_user_id = user_id
    
    def get_tools(self):
        """获取所有工具"""
        @tool
        def create_note_tool(
            title: str,
            content: str,
            category: str = "PERSONAL",
            tags: List[str] = None,
            is_pinned: bool = False,
            is_archived: bool = False
        ) -> str:
            """创建新笔记
            
            Args:
                title: 笔记标题
                content: 笔记内容
                category: 笔记分类 (PERSONAL, WORK, STUDY, IDEA, MEETING, OTHER)
                tags: 标签列表（可选）
                is_pinned: 是否置顶（默认False）
                is_archived: 是否归档（默认False）
            """
            return self._create_note_tool(title, content, category, tags, is_pinned, is_archived)
        
        @tool
        def get_notes_tool() -> str:
            """获取所有笔记"""
            return self._get_notes_tool()
        
        @tool
        def get_note_tool(id: int) -> str:
            """获取指定笔记"""
            return self._get_note_tool(id)
        
        @tool
        def update_note_tool(
            id: int,
            title: str = None,
            content: str = None,
            category: str = None,
            tags: List[str] = None,
            is_pinned: bool = None,
            is_archived: bool = None
        ) -> str:
            """更新笔记"""
            return self._update_note_tool(id, title, content, category, tags, is_pinned, is_archived)
        
        @tool
        def delete_note_tool(id: int) -> str:
            """删除指定笔记"""
            return self._delete_note_tool(id)
        
        @tool
        def search_notes_tool(
            query: str = None,
            category: str = None,
            tags: List[str] = None,
            is_pinned: bool = None,
            is_archived: bool = None,
            limit: int = 20
        ) -> str:
            """搜索笔记"""
            return self._search_notes_tool(query, category, tags, is_pinned, is_archived, limit)
        
        @tool
        def get_pinned_notes_tool() -> str:
            """获取置顶笔记"""
            return self._get_pinned_notes_tool()
        
        @tool
        def get_recent_notes_tool(days: int = 7, limit: int = 20) -> str:
            """获取最近笔记"""
            return self._get_recent_notes_tool(days, limit)
        
        @tool
        def refresh_note_list_tool() -> str:
            """刷新前端笔记列表"""
            return self._refresh_note_list_tool()
        
        return [
            create_note_tool,
            get_notes_tool,
            get_note_tool,
            update_note_tool,
            delete_note_tool,
            search_notes_tool,
            get_pinned_notes_tool,
            get_recent_notes_tool,
            refresh_note_list_tool
        ]
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取工具定义（用于模型绑定）"""
        tools = self.get_tools()
        tool_defs = []
        
        for tool in tools:
            tool_def = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.args_schema.model_json_schema() if hasattr(tool, 'args_schema') else {}
                }
            }
            tool_defs.append(tool_def)
        
        return tool_defs
    
    def _create_note_tool(
        self,
        title: str,
        content: str,
        category: str = "PERSONAL",
        tags: Optional[List[str]] = None,
        is_pinned: bool = False,
        is_archived: bool = False
    ) -> str:
        """创建新笔记"""
        try:
            # 转换分类枚举
            try:
                category_enum = NoteCategoryEnum[category.upper()]
            except KeyError:
                category_enum = NoteCategoryEnum.PERSONAL
            
            note_data = NoteCreate(
                title=title,
                content=content,
                category=category_enum,
                tags=tags or [],
                is_pinned=is_pinned,
                is_archived=is_archived
            )
            
            note = self.note_service.create_note(note_data, self.current_user_id)
            refresh_message = self._refresh_note_list_tool()
            return f'笔记创建成功: "{note.title}" (ID: {note.id}, 字数: {note.word_count})\n{refresh_message}'
        except Exception as e:
            print(f"[DEBUG] 笔记创建失败: {e}")
            import traceback
            traceback.print_exc()
            return f'笔记创建失败: {str(e)}'
    
    def _get_notes_tool(self) -> str:
        """获取所有笔记"""
        try:
            notes = self.note_service.get_all_notes(self.current_user_id)
            if not notes:
                return '没有找到笔记。'
            
            note_list = '\n'.join([
                f'- {n.id}: {n.title} ({n.category}, {n.word_count}字, {"置顶" if n.is_pinned else ""})'
                for n in notes
            ])
            return f'找到 {len(notes)} 个笔记:\n{note_list}'
        except Exception as e:
            return f'获取笔记列表失败: {str(e)}'
    
    def _get_note_tool(self, id: int) -> str:
        """获取指定笔记"""
        try:
            note = self.note_service.get_note_by_id(id, self.current_user_id)
            if not note:
                return f'未找到 ID 为 {id} 的笔记。'
            
            return f'笔记 {note.id}: "{note.title}"\n分类: {note.category}\n内容: {note.content[:200]}...\n字数: {note.word_count}'
        except Exception as e:
            return f'获取笔记失败: {str(e)}'
    
    def _update_note_tool(
        self,
        id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_pinned: Optional[bool] = None,
        is_archived: Optional[bool] = None
    ) -> str:
        """更新笔记"""
        try:
            update_data = {}
            if title is not None:
                update_data['title'] = title
            if content is not None:
                update_data['content'] = content
            if category is not None:
                try:
                    update_data['category'] = NoteCategoryEnum[category.upper()]
                except KeyError:
                    pass
            if tags is not None:
                update_data['tags'] = tags
            if is_pinned is not None:
                update_data['is_pinned'] = is_pinned
            if is_archived is not None:
                update_data['is_archived'] = is_archived
            
            if not update_data:
                return '没有提供要更新的字段。'
            
            note_update = NoteUpdate(**update_data)
            updated_note = self.note_service.update_note(id, note_update, self.current_user_id)
            
            if not updated_note:
                return f'更新笔记 {id} 失败。'
            
            refresh_message = self._refresh_note_list_tool()
            return f'笔记 {updated_note.id} 更新成功: "{updated_note.title}"\n{refresh_message}'
        except Exception as e:
            return f'更新笔记失败: {str(e)}'
    
    def _delete_note_tool(self, id: int) -> str:
        """删除指定笔记"""
        try:
            note = self.note_service.get_note_by_id(id, self.current_user_id)
            if not note:
                return f'未找到 ID 为 {id} 的笔记。'
            
            deleted = self.note_service.delete_note(id, self.current_user_id)
            if not deleted:
                return f'删除笔记 {id} 失败。'
            
            refresh_message = self._refresh_note_list_tool()
            return f'笔记 {note.id} ("{note.title}") 删除成功。\n{refresh_message}'
        except Exception as e:
            return f'删除笔记失败: {str(e)}'
    
    def _search_notes_tool(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_pinned: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        limit: int = 20
    ) -> str:
        """搜索笔记"""
        try:
            category_enum = None
            if category:
                try:
                    category_enum = NoteCategoryEnum[category.upper()]
                except KeyError:
                    pass
            
            notes = self.note_service.search_notes(
                query=query,
                category=category_enum,
                tags=tags,
                is_pinned=is_pinned,
                is_archived=is_archived,
                user_id=self.current_user_id,
                limit=limit
            )
            
            if not notes:
                return '没有找到匹配的笔记。'
            
            note_list = '\n'.join([
                f'- {n.id}: {n.title} ({n.category}, {n.word_count}字)'
                for n in notes
            ])
            return f'找到 {len(notes)} 个匹配的笔记:\n{note_list}'
        except Exception as e:
            return f'搜索笔记失败: {str(e)}'
    
    def _get_pinned_notes_tool(self) -> str:
        """获取置顶笔记"""
        try:
            notes = self.note_service.get_pinned_notes(self.current_user_id)
            if not notes:
                return '没有置顶笔记。'
            
            note_list = '\n'.join([
                f'- {n.id}: {n.title} ({n.word_count}字)'
                for n in notes
            ])
            return f'找到 {len(notes)} 个置顶笔记:\n{note_list}'
        except Exception as e:
            return f'获取置顶笔记失败: {str(e)}'
    
    def _get_recent_notes_tool(self, days: int = 7, limit: int = 20) -> str:
        """获取最近笔记"""
        try:
            notes = self.note_service.get_recent_notes(days, limit, self.current_user_id)
            if not notes:
                return f'最近 {days} 天没有创建笔记。'
            
            note_list = '\n'.join([
                f'- {n.id}: {n.title} ({n.word_count}字, {n.created_at.strftime("%Y-%m-%d")})'
                for n in notes
            ])
            return f'找到 {len(notes)} 个最近笔记:\n{note_list}'
        except Exception as e:
            return f'获取最近笔记失败: {str(e)}'
    
    def _refresh_note_list_tool(self) -> str:
        """刷新前端笔记列表"""
        try:
            return 'frontend_tool_call:refresh_note_list 正在为您刷新笔记列表...'
        except Exception as e:
            return f'前端刷新失败: {str(e)}'

