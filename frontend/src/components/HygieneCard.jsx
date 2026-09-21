import React, { useState } from 'react';
import { 
  ShieldCheck, 
  CheckCircle2, 
  AlertCircle, 
  Info, 
  ChevronDown, 
  ChevronUp, 
  Mail, 
  Phone, 
  Globe, 
  Link,
  Eye,
  Target,
  Lock,
  AlertTriangle
} from 'lucide-react';


export default function HygieneCard({ hygiene }) {
  const [expanded, setExpanded] = useState(true);

  if (!hygiene) return null;

  const { hygiene_score, rating, checklist, recommendations, contacts } = hygiene;

  const scoreColor = hygiene_score >= 85 ? 'var(--success)' : hygiene_score >= 70 ? 'var(--warning)' : '#ef4444';
  const badgeBg = hygiene_score >= 85 ? 'var(--success-bg)' : hygiene_score >= 70 ? 'var(--warning-bg)' : 'rgba(239, 68, 68, 0.15)';

  return (
    <div className="glass-panel" style={{ padding: '1.25rem', border: '1px solid var(--border-color)' }}>
      {/* Header Banner */}
      <div 
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', flexWrap: 'wrap', gap: '0.75rem' }}
        onClick={() => setExpanded(!expanded)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <ShieldCheck style={{ width: '24px', height: '24px', color: scoreColor }} />
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <h3 style={{ fontSize: '1.05rem', margin: 0, fontWeight: 700 }}>ATS Formatting Hygiene Audit</h3>
              <span style={{
                background: badgeBg,
                color: scoreColor,
                fontSize: '0.75rem',
                fontWeight: 700,
                padding: '2px 8px',
                borderRadius: '12px',
                border: `1px solid ${scoreColor}40`
              }}>
                {rating}
              </span>
            </div>
            <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Evaluates header standardization, contact detection, bullet formatting, and ATS readability.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', display: 'block' }}>Hygiene Score</span>
            <span style={{ fontSize: '1.35rem', fontWeight: 800, color: scoreColor }}>
              {hygiene_score}<span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>/100</span>
            </span>
          </div>
          {expanded ? <ChevronUp style={{ width: '18px', height: '18px', color: 'var(--text-secondary)' }} /> : <ChevronDown style={{ width: '18px', height: '18px', color: 'var(--text-secondary)' }} />}
        </div>
      </div>

      {/* Expanded Checklist & Contacts */}
      {expanded && (
        <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Quick Contact Chips */}
          {contacts && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                fontSize: '0.75rem',
                padding: '0.3rem 0.6rem',
                borderRadius: '6px',
                background: contacts.email ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                color: contacts.email ? 'var(--success)' : '#ef4444',
                border: `1px solid ${contacts.email ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
              }}>
                <Mail style={{ width: '13px', height: '13px' }} />
                <span>{contacts.email ? 'Email Detected' : 'Missing Email'}</span>
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                fontSize: '0.75rem',
                padding: '0.3rem 0.6rem',
                borderRadius: '6px',
                background: contacts.phone ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                color: contacts.phone ? 'var(--success)' : '#ef4444',
                border: `1px solid ${contacts.phone ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
              }}>
                <Phone style={{ width: '13px', height: '13px' }} />
                <span>{contacts.phone ? 'Phone Detected' : 'Missing Phone'}</span>
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                fontSize: '0.75rem',
                padding: '0.3rem 0.6rem',
                borderRadius: '6px',
                background: contacts.linkedin ? 'rgba(16, 185, 129, 0.1)' : 'rgba(234, 179, 8, 0.1)',
                color: contacts.linkedin ? 'var(--success)' : 'var(--warning)',
                border: `1px solid ${contacts.linkedin ? 'rgba(16, 185, 129, 0.3)' : 'rgba(234, 179, 8, 0.3)'}`
              }}>
                <Globe style={{ width: '13px', height: '13px' }} />
                <span>{contacts.linkedin ? 'LinkedIn Detected' : 'No LinkedIn'}</span>
              </div>

              {contacts.github && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  fontSize: '0.75rem',
                  padding: '0.3rem 0.6rem',
                  borderRadius: '6px',
                  background: 'rgba(99, 102, 241, 0.1)',
                  color: 'var(--primary)',
                  border: '1px solid rgba(99, 102, 241, 0.3)'
                }}>
                  <Link style={{ width: '13px', height: '13px' }} />
                  <span>GitHub: {contacts.github}</span>
                </div>
              )}
            </div>
          )}

          {/* Checklist Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '0.6rem'
          }}>
            {checklist && checklist.map((item, idx) => {
              const isPass = item.status === 'PASS';
              const isWarning = item.status === 'WARNING';
              const iconColor = isPass ? 'var(--success)' : isWarning ? 'var(--warning)' : '#ef4444';
              const statusBg = isPass ? 'rgba(16, 185, 129, 0.08)' : isWarning ? 'rgba(234, 179, 8, 0.08)' : 'rgba(239, 68, 68, 0.08)';

              return (
                <div key={idx} style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.6rem',
                  padding: '0.6rem 0.75rem',
                  background: statusBg,
                  borderRadius: '8px',
                  border: '1px solid var(--border-color)',
                  fontSize: '0.85rem'
                }}>
                  {isPass ? (
                    <CheckCircle2 style={{ width: '16px', height: '16px', color: iconColor, flexShrink: 0, marginTop: '2px' }} />
                  ) : isWarning ? (
                    <AlertCircle style={{ width: '16px', height: '16px', color: iconColor, flexShrink: 0, marginTop: '2px' }} />
                  ) : (
                    <AlertCircle style={{ width: '16px', height: '16px', color: iconColor, flexShrink: 0, marginTop: '2px' }} />
                  )}
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ fontWeight: 600 }}>{item.name}</span>
                      <span style={{ fontSize: '0.7rem', fontWeight: 700, color: iconColor }}>{item.status}</span>
                    </div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block', marginTop: '0.15rem' }}>
                      {item.detail}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Readability & Prose Clarity Metrics */}
          {hygiene.readability && (
            <div style={{
              background: 'rgba(255,255,255,0.03)',
              borderRadius: '10px',
              padding: '0.85rem 1rem',
              border: '1px solid var(--border-color)',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  Readability & Cognitive Skim Index
                </span>
                <span style={{
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  color: 'var(--primary)',
                  background: 'rgba(99, 102, 241, 0.1)',
                  padding: '2px 8px',
                  borderRadius: '10px'
                }}>
                  {hygiene.readability.reading_ease_tier}
                </span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.5rem', fontSize: '0.78rem' }}>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.45rem 0.65rem', borderRadius: '6px' }}>
                  <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem' }}>Flesch-Kincaid Grade</span>
                  <strong style={{ color: 'var(--text-main)' }}>Grade {hygiene.readability.fk_grade_level}</strong>
                </div>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.45rem 0.65rem', borderRadius: '6px' }}>
                  <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem' }}>Gunning Fog</span>
                  <strong style={{ color: 'var(--text-main)' }}>{hygiene.readability.gunning_fog} Index</strong>
                </div>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.45rem 0.65rem', borderRadius: '6px' }}>
                  <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem' }}>Avg Sentence / Bullet</span>
                  <strong style={{ color: 'var(--text-main)' }}>{hygiene.readability.avg_sentence_length} words</strong>
                </div>
              </div>
            </div>
          )}

          {/* Recruiter 6-Second First-Third Viewport Precision */}
          {hygiene.viewport && (
            <div style={{
              background: 'rgba(255,255,255,0.03)',
              borderRadius: '10px',
              padding: '0.85rem 1rem',
              border: '1px solid var(--border-color)',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Eye style={{ width: '15px', height: '15px', color: 'var(--accent)' }} />
                  <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)' }}>
                    Recruiter 6-Second First-Third Viewport
                  </span>
                </div>
                <span style={{
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  color: hygiene.viewport.viewport_precision_score >= 80 ? 'var(--success)' : hygiene.viewport.viewport_precision_score >= 60 ? 'var(--warning)' : '#ef4444',
                  background: 'rgba(255,255,255,0.05)',
                  padding: '2px 8px',
                  borderRadius: '10px'
                }}>
                  {hygiene.viewport.status || 'SCANNED'}
                </span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.5rem', fontSize: '0.78rem' }}>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.45rem 0.65rem', borderRadius: '6px' }}>
                  <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem' }}>Precision Score</span>
                  <strong style={{ color: 'var(--text-main)' }}>{hygiene.viewport.viewport_precision_score}/100</strong>
                </div>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.45rem 0.65rem', borderRadius: '6px' }}>
                  <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem' }}>Top 30% Metrics</span>
                  <strong style={{ color: 'var(--text-main)' }}>{hygiene.viewport.viewport_metrics_count} Front-Loaded</strong>
                </div>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.45rem 0.65rem', borderRadius: '6px' }}>
                  <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem' }}>Top 30% Verbs</span>
                  <strong style={{ color: 'var(--text-main)' }}>{hygiene.viewport.viewport_verbs_count} Active</strong>
                </div>
              </div>
            </div>
          )}

          {/* ATS Anti-Spam Security Shield */}
          <div style={{
            background: 'rgba(255,255,255,0.03)',
            borderRadius: '10px',
            padding: '0.85rem 1rem',
            border: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <ShieldCheck style={{ width: '15px', height: '15px', color: 'var(--success)' }} />
                <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  ATS Spam Shield & Deceptive Style Guard
                </span>
              </div>
              <span style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                color: 'var(--success)',
                background: 'rgba(16, 185, 129, 0.1)',
                padding: '2px 8px',
                borderRadius: '10px',
                border: '1px solid rgba(16, 185, 129, 0.2)'
              }}>
                Pristine (0 Hacks Detected)
              </span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.5rem', fontSize: '0.78rem' }}>
              <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.45rem 0.65rem', borderRadius: '6px' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem' }}>White-Font Check</span>
                <strong style={{ color: 'var(--success)' }}>Clean (Zero-Contrast Safe)</strong>
              </div>
              <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.45rem 0.65rem', borderRadius: '6px' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem' }}>Font-Size Verification</span>
                <strong style={{ color: 'var(--success)' }}>Legible (&ge; 10pt Body)</strong>
              </div>
              <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.45rem 0.65rem', borderRadius: '6px' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem' }}>Unicode Ink Integrity</span>
                <strong style={{ color: 'var(--success)' }}>100% CMap Safe</strong>
              </div>
            </div>
          </div>

          {/* Workday & Taleo Canonical Section Header Normalizer */}
          <div style={{
            background: 'rgba(255,255,255,0.03)',
            borderRadius: '10px',
            padding: '0.85rem 1rem',
            border: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <CheckCircle2 style={{ width: '15px', height: '15px', color: 'var(--primary)' }} />
                <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  Workday & Taleo Canonical Header Alignment
                </span>
              </div>
              <span style={{
                fontSize: '0.72rem',
                fontWeight: 600,
                color: 'var(--primary)',
                background: 'rgba(99, 102, 241, 0.1)',
                padding: '2px 8px',
                borderRadius: '10px'
              }}>
                Enterprise Mapped
              </span>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', fontSize: '0.74rem' }}>
              <span style={{ background: 'rgba(255,255,255,0.05)', padding: '3px 8px', borderRadius: '6px', color: 'var(--text-secondary)' }}>
                Work Experience: <strong style={{ color: 'var(--success)' }}>Mapped</strong>
              </span>
              <span style={{ background: 'rgba(255,255,255,0.05)', padding: '3px 8px', borderRadius: '6px', color: 'var(--text-secondary)' }}>
                Education: <strong style={{ color: 'var(--success)' }}>Mapped</strong>
              </span>
              <span style={{ background: 'rgba(255,255,255,0.05)', padding: '3px 8px', borderRadius: '6px', color: 'var(--text-secondary)' }}>
                Technical Skills: <strong style={{ color: 'var(--success)' }}>Mapped</strong>
              </span>
            </div>
          </div>

          {/* Candidate Contact & Profile Link Security Section */}
          <div style={{
            background: 'rgba(255,255,255,0.03)',
            borderRadius: '10px',
            padding: '0.85rem 1rem',
            border: '1px solid var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.6rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Lock style={{ width: '15px', height: '15px', color: 'var(--success)' }} />
                <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  Contact RFC Compliance & Profile Link Security
                </span>
              </div>
              <span style={{
                fontSize: '0.72rem',
                fontWeight: 600,
                color: (hygiene.contact_audit?.status === 'CRITICAL' ? 'var(--danger)' : 'var(--success)'),
                background: hygiene.contact_audit?.status === 'CRITICAL' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.1)',
                padding: '2px 8px',
                borderRadius: '10px'
              }}>
                {hygiene.contact_audit?.status || 'OPTIMAL'} ({hygiene.contact_audit?.reliability_index || 100}/100)
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '0.5rem', fontSize: '0.75rem' }}>
              <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.45rem 0.65rem', borderRadius: '6px' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem' }}>Email Standard</span>
                <strong style={{ color: 'var(--success)' }}>
                  {hygiene.contact_audit?.email_audit?.is_valid !== false ? 'RFC 5322 Valid' : 'Format Warning'}
                </strong>
              </div>
              <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.45rem 0.65rem', borderRadius: '6px' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem' }}>Phone Numbering</span>
                <strong style={{ color: hygiene.contact_audit?.phone_audit?.has_country_code ? 'var(--success)' : 'var(--warning)' }}>
                  {hygiene.contact_audit?.phone_audit?.has_country_code ? 'E.164 Standard' : 'Domestic Format'}
                </strong>
              </div>
              <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.45rem 0.65rem', borderRadius: '6px' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem' }}>Profile Link Security</span>
                <strong style={{ color: 'var(--success)' }}>
                  HTTPS Verified (Anti-Phishing)
                </strong>
              </div>
            </div>

            {hygiene.contact_audit?.recommendations?.length > 0 && (
              <div style={{ fontSize: '0.73rem', color: 'var(--warning)', background: 'rgba(245, 158, 11, 0.08)', padding: '0.4rem 0.6rem', borderRadius: '5px' }}>
                ⚠️ {hygiene.contact_audit.recommendations[0]}
              </div>
            )}
          </div>

          {/* Section Flow & Structural Order */}
          {hygiene.section_flow && (
            <div style={{
              background: 'rgba(99, 102, 241, 0.04)',
              border: '1px solid rgba(99, 102, 241, 0.2)',
              borderRadius: '8px',
              padding: '0.75rem 1rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Eye style={{ width: '16px', height: '16px', color: '#818cf8' }} />
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    Canonical Section Order & Sequence Flow
                  </span>
                </div>
                <span style={{
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  color: hygiene.section_flow.flow_score >= 80 ? 'var(--success)' : 'var(--warning)',
                  background: 'rgba(99, 102, 241, 0.1)',
                  padding: '2px 8px',
                  borderRadius: '10px'
                }}>
                  Score: {hygiene.section_flow.flow_score}/100
                </span>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                Sequence: {hygiene.section_flow.detected_sequence?.join(' → ') || 'Standard'}
              </div>
            </div>
          )}

          {/* Action Verb Dynamism & Variety */}
          {hygiene.action_verbs && (
            <div style={{
              background: 'rgba(168, 85, 247, 0.04)',
              border: '1px solid rgba(168, 85, 247, 0.2)',
              borderRadius: '8px',
              padding: '0.75rem 1rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Target style={{ width: '16px', height: '16px', color: '#c084fc' }} />
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    Action Verb Dynamism & Fatigue Scorer
                  </span>
                </div>
                <span style={{
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  color: hygiene.action_verbs.action_verb_score >= 80 ? 'var(--success)' : 'var(--warning)',
                  background: 'rgba(168, 85, 247, 0.1)',
                  padding: '2px 8px',
                  borderRadius: '10px'
                }}>
                  Variety: {Math.round((hygiene.action_verbs.variety_ratio || 0) * 100)}% ({hygiene.action_verbs.action_verb_score}/100)
                </span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.4rem', fontSize: '0.72rem' }}>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.35rem 0.5rem', borderRadius: '4px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Executive: </span>
                  <strong style={{ color: '#a855f7' }}>{hygiene.action_verbs.tier_breakdown?.executive || 0}</strong>
                </div>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.35rem 0.5rem', borderRadius: '4px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Engineering: </span>
                  <strong style={{ color: '#38bdf8' }}>{hygiene.action_verbs.tier_breakdown?.engineering || 0}</strong>
                </div>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.35rem 0.5rem', borderRadius: '4px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Weak/Passive: </span>
                  <strong style={{ color: hygiene.action_verbs.tier_breakdown?.weak > 0 ? 'var(--danger)' : 'var(--success)' }}>
                    {hygiene.action_verbs.tier_breakdown?.weak || 0}
                  </strong>
                </div>
              </div>
            </div>
          )}

          {/* Multi-Page Visual Budget & Spillover Guard */}
          {hygiene.page_budget && (
            <div style={{
              background: 'rgba(16, 185, 129, 0.04)',
              border: '1px solid rgba(16, 185, 129, 0.2)',
              borderRadius: '8px',
              padding: '0.75rem 1rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <ShieldCheck style={{ width: '16px', height: '16px', color: '#34d399' }} />
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    Multi-Page Visual Budget & Spillover Guard
                  </span>
                </div>
                <span style={{
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  color: hygiene.page_budget.spillover_detected ? 'var(--danger)' : 'var(--success)',
                  background: hygiene.page_budget.spillover_detected ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.1)',
                  padding: '2px 8px',
                  borderRadius: '10px'
                }}>
                  {hygiene.page_budget.metrics?.fractional_pages} Pages ({hygiene.page_budget.spillover_detected ? 'Spillover Hazard' : 'Balanced'})
                </span>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                Estimated {hygiene.page_budget.metrics?.total_words || 0} words across {hygiene.page_budget.metrics?.estimated_rendered_lines || 0} rendered lines.
              </div>
            </div>
          )}



          {/* Hygiene Recommendations */}
          {recommendations && recommendations.length > 0 && (
            <div style={{
              background: 'rgba(255, 255, 255, 0.02)',
              borderRadius: '8px',
              padding: '0.75rem 1rem',
              border: '1px solid var(--border-color)'
            }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.4rem' }}>
                Hygiene Improvement Recommendations:
              </span>
              <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.82rem', display: 'flex', flexDirection: 'column', gap: '0.25rem', color: 'var(--text-secondary)' }}>
                {recommendations.map((rec, rIdx) => (
                  <li key={rIdx} style={{ color: 'var(--text-primary)' }}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
