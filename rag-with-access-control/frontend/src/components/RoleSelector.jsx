import { User, ChevronRight, Loader } from "lucide-react";
import "./RoleSelector.css";

const RoleSelector = ({
  roles,
  selectedRole,
  onRoleSelect,
  onContinue,
  loading,
}) => {
  return (
    <div className="role-selector">
      <div className="role-selector-header">
        <div className="role-selector-badge">
          <User className="title-icon" />
        </div>
        <h2 className="role-selector-title">Select Your Role</h2>
        <p className="role-selector-subtitle">
          Choose the appropriate access level for your needs
        </p>
      </div>

      <div className="roles-container">
        {roles.map((role) => (
          <div
            key={role.id}
            className={`role-option ${
              selectedRole === role.id ? "selected" : ""
            }`}
            onClick={() => onRoleSelect(role.id)}
          >
            <div className={`role-icon ${role.id}`}>{role.icon}</div>
            <div className="role-content">
              <h3 className="role-name">{role.name}</h3>
              <p className="role-description">{role.description}</p>
            </div>
            {selectedRole === role.id ? (
              <div className="role-selected-indicator">
                <ChevronRight size={16} />
              </div>
            ) : (
              <div className="radio-circle"></div>
            )}
          </div>
        ))}
      </div>

      <button
        className={`continue-button ${selectedRole ? "active" : ""}`}
        onClick={onContinue}
        disabled={!selectedRole || loading}
      >
        {loading ? (
          <>
            <Loader className="spinner" size={16} /> 
            <span>Authenticating...</span>
          </>
        ) : (
          <span>Continue</span>
        )}
      </button>
      
      <div className="role-selector-tips">
        <p>Each role provides different access levels to company information</p>
      </div>
    </div>
  );
};

export default RoleSelector;
