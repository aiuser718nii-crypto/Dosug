import { useState, useEffect } from 'react';
import { groupService } from '../services/api';
import { subjectService } from '../services/api';
import GroupList from '../components/groups/GroupList';
import GroupForm from '../components/groups/GroupForm';
import toast from 'react-hot-toast';

export default function Groups() {
  const [groups, setGroups] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingGroup, setEditingGroup] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [groupsData, subjectsData] = await Promise.all([
        groupService.getAll(),
        subjectService.getAll()
      ]);
      setGroups(groupsData);
      setSubjects(subjectsData);
    } catch (error) {
      toast.error('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (data) => {
    try {
      await groupService.create(data);
      toast.success('Группа добавлена');
      loadData();
      setShowForm(false);
    } catch (error) {
      toast.error('Ошибка при добавлении');
    }
  };

  const handleEdit = (group) => {
    setEditingGroup(group);
    setShowForm(true);
  };

  const handleUpdate = async (id, data) => {
    try {
      await groupService.update(id, data);
      toast.success('Группа обновлена');
      loadData();
      setShowForm(false);
      setEditingGroup(null);
    } catch (error) {
      toast.error('Ошибка при обновлении');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Удалить группу? Это также удалит связанные с ней расписания.')) return;
    
    try {
      await groupService.delete(id);
      toast.success('Группа удалена');
      loadData();
    } catch (error) {
      toast.error('Ошибка при удалении');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Группы студентов</h1>
          <p className="text-gray-500 mt-1">
            Управление группами и их предметами
          </p>
        </div>
        <button
          onClick={() => {
            setEditingGroup(null);
            setShowForm(true);
          }}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <span>+</span>
          <span>Добавить группу</span>
        </button>
      </div>

      {showForm && (
        <GroupForm
          group={editingGroup}
          subjects={subjects}
          onSubmit={editingGroup 
            ? (data) => handleUpdate(editingGroup.id, data)
            : handleCreate
          }
          onCancel={() => {
            setShowForm(false);
            setEditingGroup(null);
          }}
        />
      )}

      <GroupList
        groups={groups}
        loading={loading}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
}