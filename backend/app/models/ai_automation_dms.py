from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, Index, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class QMSDocument(Base):
    '''Master Control Documents - SOPs, Work Instructions, Forms'''
    __tablename__ = 'qms_documents'
    
    id = Column(String(36), primary_key=True)
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False)  # SOP, WorkInstruction, Form, Template
    document_version = Column(String(20), nullable=False)
    file_path = Column(String(255))
    file_format = Column(String(20))  # PDF, DOCX, TXT
    content_hash = Column(String(64))  # SHA256
    raw_content = Column(LargeBinary)  # Compressed content
    extracted_text = Column(Text)  # Plain text extraction
    uploaded_by = Column(String(36), ForeignKey('users.id'), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    approval_status = Column(String(50), default='DRAFT')  # DRAFT, APPROVED, SUPERSEDED
    approved_by = Column(String(36), ForeignKey('users.id'))
    approved_at = Column(DateTime)
    effective_date = Column(DateTime)
    review_date = Column(DateTime)
    
    ai_extractions = relationship('AIExtraction', back_populates='source_document')
    ai_templates = relationship('AITemplate', back_populates='source_document')
    __table_args__ = (Index('idx_doc_type', 'document_type'),)

class AIExtraction(Base):
    '''AI-extracted data from QMS documents using GPT-4'''
    __tablename__ = 'ai_extractions'
    
    id = Column(String(36), primary_key=True)
    source_document_id = Column(String(36), ForeignKey('qms_documents.id'), nullable=False)
    extraction_type = Column(String(50), nullable=False)  # Requirement, Process, Risk, Responsibility
    extracted_text = Column(Text, nullable=False)
    confidence_score = Column(Float)  # 0-100 from AI model
    extraction_metadata = Column(JSON)  # Tags, entities, context
    ai_model_version = Column(String(50))  # GPT-4, Claude, etc.
    extracted_at = Column(DateTime, default=datetime.utcnow)
    is_validated = Column(Boolean, default=False)
    validated_by = Column(String(36), ForeignKey('users.id'))
    validated_at = Column(DateTime)
    validation_notes = Column(Text)
    
    source_document = relationship('QMSDocument', back_populates='ai_extractions')
    requirements = relationship('RequirementExtraction', back_populates='extraction')
    __table_args__ = (Index('idx_confidence', 'confidence_score'),)

class RequirementExtraction(Base):
    '''Extracted requirements with auto-linking to test plans'''
    __tablename__ = 'requirement_extractions'
    
    id = Column(String(36), primary_key=True)
    ai_extraction_id = Column(String(36), ForeignKey('ai_extractions.id'), nullable=False)
    requirement_text = Column(Text, nullable=False)
    requirement_category = Column(String(50))  # Functional, Performance, Security, Compliance
    requirement_priority = Column(String(20))  # High, Medium, Low
    acceptance_criteria = Column(JSON)  # List of AC from document
    risk_assessment = Column(JSON)  # Associated risks
    linked_test_plan_id = Column(String(36), ForeignKey('test_plans.id'))
    linked_requirement_id = Column(String(36), ForeignKey('requirements.id'))
    auto_generated = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    extraction = relationship('AIExtraction', back_populates='requirements')

class AITemplate(Base):
    '''AI-generated validation templates from QMS documents'''
    __tablename__ = 'ai_templates'
    
    id = Column(String(36), primary_key=True)
    template_name = Column(String(255), nullable=False)
    source_document_id = Column(String(36), ForeignKey('qms_documents.id'))
    template_type = Column(String(50), nullable=False)  # TestPlan, ValidationPlan, TestCase, RTM
    template_content = Column(JSON)  # Full template structure
    generation_metadata = Column(JSON)  # How it was generated
    ai_quality_score = Column(Float)  # Quality: 0-100
    generated_at = Column(DateTime, default=datetime.utcnow)
    business_approved = Column(Boolean, default=False)
    business_approved_by = Column(String(36), ForeignKey('users.id'))
    ready_for_production = Column(Boolean, default=False)
    migration_status = Column(String(50))  # NOT_MIGRATED, MIGRATED, IN_PRODUCTION
    migrated_to_dms_id = Column(String(36))  # Link to DMS after migration
    
    source_document = relationship('QMSDocument', back_populates='ai_templates')
    __table_args__ = (Index('idx_quality_status', 'ai_quality_score', 'migration_status'),)

class DMSDocument(Base):
    '''New Document Management System - migrated from QMS'''
    __tablename__ = 'dms_documents'
    
    id = Column(String(36), primary_key=True)
    source_qms_document_id = Column(String(36), ForeignKey('qms_documents.id'))
    document_title = Column(String(255), nullable=False)
    document_code = Column(String(50), unique=True)
    document_type = Column(String(50))  # SOP, WorkInstruction, etc.
    version_number = Column(Integer, default=1)
    lifecycle_status = Column(String(50))  # Draft, Under Review, Approved, In Use, Archived
    content_json = Column(JSON)  # Structured document
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(36), ForeignKey('users.id'))
    approval_chain = Column(JSON)  # Approval workflow history
    is_locked = Column(Boolean, default=False)
    change_request_id = Column(String(36))  # Link to change request
    
    __table_args__ = (Index('idx_lifecycle', 'lifecycle_status'),)
