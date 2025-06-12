import { Shield, FileText, Users, Globe } from "lucide-react";
import "./AccessControlPanel.css";

const AccessControlPanel = ({ selectedRole, roles }) => {
  const getAccessDetails = (roleId) => {
    const accessMap = {
      hr: {
        documents: [
          "Employee records",
          "Performance evaluations",
          "Salary information",
          "HR policies and procedures",
        ],
        permissions: [
          "Access employee data",
          "View compensation details",
          "Read performance metrics",
        ],
      },
      engineering: {
        documents: [
          "API documentation",
          "Code repositories",
          "Architecture diagrams",
          "Technical specifications",
        ],
        permissions: [
          "Access technical documentation",
          "View system architecture",
          "Read development guidelines",
        ],
      },
      public: {
        documents: [
          "Public announcements",
          "Company information",
          "General resources",
          "Contact information",
        ],
        permissions: [
          "Access public information",
          "View company announcements",
          "Read general documentation",
        ],
      },
    };
    return accessMap[roleId] || { documents: [], permissions: [] };
  };

  const selectedRoleData = roles.find((role) => role.id === selectedRole);
  const accessDetails = getAccessDetails(selectedRole);

  return (
    <div className="access-control-panel">
      <div className="panel-header">
        <Shield className="panel-icon" />
        <h2 className="panel-title">Document Access Control</h2>
        <p className="panel-subtitle">Select your role to continue</p>
      </div>

      <div className="access-sections">
        {selectedRole ? (
          <>
            <div className="selected-role-info">
              <div className="role-badge">
                <span className="role-badge-icon">
                  {selectedRoleData?.icon}
                </span>
                <div className="role-badge-content">
                  <h3 className="role-badge-title">{selectedRoleData?.name}</h3>
                  <p className="role-badge-description">
                    {selectedRoleData?.description}
                  </p>
                </div>
              </div>
            </div>

            <div className="access-section">
              <div className="section-header">
                <FileText className="section-icon" />
                <h3 className="section-title">Available Documents</h3>
              </div>
              <ul className="access-list">
                {accessDetails.documents.map((doc, index) => (
                  <li key={index} className="access-item">
                    <div className="access-dot"></div>
                    {doc}
                  </li>
                ))}
              </ul>
            </div>

            <div className="access-section">
              <div className="section-header">
                <Users className="section-icon" />
                <h3 className="section-title">Access Permissions</h3>
              </div>
              <ul className="access-list">
                {accessDetails.permissions.map((permission, index) => (
                  <li key={index} className="access-item">
                    <div className="access-dot"></div>
                    {permission}
                  </li>
                ))}
              </ul>
            </div>
          </>
        ) : (
          <div className="no-selection">
            <Globe className="no-selection-icon" />
            <h3 className="no-selection-title">No Role Selected</h3>
            <p className="no-selection-text">
              Please select a role from the left panel to view access
              permissions and available documents.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AccessControlPanel;
