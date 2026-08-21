# Platform Requirements Documentation

**Last Updated**: 2026-07-08
**Platform Versions**: LinkedIn 2026, X 2026, Mastodon 4.x
**Purpose**: Comprehensive guide for posting content to LinkedIn, X (Twitter), and Mastodon

---

## Table of Contents

1. [Platform Overview](#platform-overview)
2. [Character Limits](#character-limits)
3. [Field Requirements](#field-requirements)
4. [Authentication & Rate Limits](#authentication--rate-limits)
5. [Content Sharing Advice](#content-sharing-advice)
6. [Cultural Norms & Formatting](#cultural-norms--formatting)
7. [Examples and Best Practices](#examples-and-best-practices)
8. [Content Adaptation Workflow](#content-adaptation-workflow)
9. [Do's and Don'ts](#do-s-and-don-ts)

---

## Platform Overview

### LinkedIn

**Tone**: Professional, informative, respectful
**Format**: Title + Summary + Tags (for posts)
**Link Requirement**: Must include "See full article" link
**Best Practices**: 2-4 sentences per post, professional formatting, paragraph breaks for readability

### X (Twitter)

**Tone**: Short, punchy, conversational
**Format**: Single tweet or thread (max 3 hashtags)
**Hashtags**: camelCase (#MachineLearning #AI)
**Best Practices**: Strong hook in first line, brevity-focused, engagement-focused

### Mastodon

**Tone**: Community-focused, slower pace
**Format**: Current behavior maintained (no changes to existing behavior)
**Markdown**: Supported, plain text preferred
**Best Practices**: Community-focused, community guidelines followed

---

## Character Limits

### Quick Reference Table

| Platform | Content Type | Character Limit |
|----------|--------------|-----------------|
| LinkedIn | Title | 300 characters |
| LinkedIn | Summary | 3000 characters |
| LinkedIn | Tags | Max 5 tags, max 25 characters each |
| X | Tweet | 280 characters |
| X | Thread Starter | 100 characters |
| X | Thread Continuation | 100 characters |
| Mastodon | Toot | 500 characters |
| Mastodon | Status | 500 characters |
| Mastodon | Note | 500 characters |

---

## Field Requirements

### LinkedIn

**Required Fields**:
- **Title**: Title of the post (max 300 characters)
- **Summary**: Main content (max 3000 characters)
- **Tags**: Optional, but recommended (max 5 tags, max 25 characters each)

**Optional Fields**:
- Article link: Must include "See full article" link if posting article

**Formatting Rules**:
- No trailing period in title
- Paragraph breaks for readability (2-4 sentences per paragraph)
- Professional tone
- Markdown or plain text supported

### X (Twitter)

**Required Fields**:
- **Content**: Main content of the tweet (max 280 characters for standard tweet)

**Optional Fields**:
- Hashtags: Up to 3 hashtags per tweet (max 280 characters total)
- Thread starter: Max 100 characters
- Thread continuation: Max 100 characters

**Formatting Rules**:
- camelCase hashtags (#MachineLearning #AI)
- No paragraph breaks (single continuous text)
- Strong hook in first line
- Short and punchy
- Conversational tone

### Mastodon

**Required Fields**:
- **Content**: Main content of the toot (max 500 characters)

**Optional Fields**:
- Hashtags: Similar to X (camelCase, max 3 hashtags per post)

**Formatting Rules**:
- Markdown supported
- Plain text preferred
- Community-focused tone
- Follow community guidelines

---

## Authentication & Rate Limits

### Authentication Requirements

**LinkedIn**:
- OAuth 2.0 flow required
- Secure token storage required
- Easy reauthentication from management panel
- Token refresh mechanism

**X (Twitter)**:
- OAuth 2.0 flow required
- Secure token storage required
- Easy reauthentication from management panel
- Token refresh mechanism

**Mastodon**:
- OAuth 2.0 flow or API token
- Secure token storage required
- Easy reauthentication from management panel
- Token refresh mechanism

### Rate Limits

| Platform | Rate Limit | Backoff Strategy |
|----------|------------|------------------|
| LinkedIn | 1-2 posts per day per account | Exponential backoff, max 5 minute delay |
| X | 10 posts per day per account | Exponential backoff, max 5 minute delay |
| Mastodon | 1 post per 2 minutes per account | Exponential backoff, max 5 minute delay |

### Token Management

- **Storage**: Environment variables or encrypted vault (e.g., HashiCorp Vault, AWS Secrets Manager)
- **Encryption**: Tokens encrypted before storage
- **Expiry Detection**: Tokens checked for expiry
- **Auto-refresh**: Tokens automatically refreshed before expiry
- **Reauthentication**: Easy reauthentication from management panel

---

## Content Sharing Advice

### LinkedIn

**When to Post**:
- Share article links with professional context
- Share research findings with detailed explanation
- Share company updates with industry insights

**Tone Guidelines**:
- Professional and informative
- Respectful of audience
- Focus on value and insights
- Avoid overly promotional language

**Link Handling**:
- Must include "See full article" link
- Provide context before the link
- Keep link concise

**Frequency**:
- Max 1-2 posts per day per account
- Best times: Weekday mornings (9-11 AM), Weekday afternoons (2-4 PM)

### X (Twitter)

**When to Post**:
- Share breaking news
- Share short insights
- Share opinions and commentary
- Share links to articles (thread format preferred)

**Tone Guidelines**:
- Short and punchy
- Conversational
- Engagement-focused
- Avoid promotional language

**Thread Strategy**:
- Use threads for longer content
- Strong hook in first line
- Clear structure (1, 2, 3...)
- Encourage replies

**Frequency**:
- Max 10 tweets per day per account
- Best times: Weekday mornings (8-10 AM), Weekday afternoons (2-4 PM)

**Hashtag Strategy**:
- Max 3 hashtags per tweet
- Use camelCase (#MachineLearning #AI)
- Reuse popular tags

### Mastodon

**When to Post**:
- Share links to articles
- Share research findings
- Share community updates
- Share long-form content

**Tone Guidelines**:
- Community-focused
- Informative
- Respectful
- Follow community guidelines

**Hashtag Strategy**:
- Similar to X (camelCase, max 3 hashtags)
- Use relevant tags

**Frequency**:
- Max 30 posts per day per account (but 1 post per 2 minutes recommended)
- Best times: Weekday mornings (9-11 AM), Weekday afternoons (2-4 PM)

**Community Guidelines**:
- Follow Mastodon-specific community guidelines
- Be respectful of all users
- Avoid harassment
- Engage with community

---

## Cultural Norms & Formatting

### LinkedIn

**Cultural Norms**:
- Professional and respectful
- Focus on insights and value
- Avoid overly promotional language
- Engage with comments professionally

**Formatting Rules**:
- Use paragraph breaks for readability
- Keep sentences relatively short (2-4 sentences per paragraph)
- Use bullet points for lists
- Use bold text for emphasis (sparingly)
- No trailing period in title

**Emoji Usage**:
- Use professional emojis (dots, checkmarks)
- Use sparingly (avoid excessive emojis)

**Link Handling**:
- Always include "See full article" link
- Provide context before the link
- Keep link concise

### X (Twitter)

**Cultural Norms**:
- Conversational and engaging
- Short and punchy
- Avoid promotional language
- Engagement-focused (reply, retweet, like)

**Formatting Rules**:
- No paragraph breaks (single continuous text)
- Use line breaks for threads
- camelCase hashtags (#MachineLearning #AI)
- No trailing period in most cases

**Emoji Usage**:
- Use friendly emojis (sparingly)
- Avoid excessive emojis
- Use in thread starters

**Thread Creation**:
- Strong hook in first line
- Clear structure (1, 2, 3...)
- Encourage replies
- Thread starter: max 100 characters
- Thread continuation: max 100 characters

**Hashtag Strategy**:
- Max 3 hashtags per tweet
- Use camelCase (#MachineLearning #AI)
- Reuse popular tags
- Use relevant tags

### Mastodon

**Cultural Norms**:
- Community-focused
- Slower pace than X
- Respectful and informative
- Follow community guidelines

**Formatting Rules**:
- Markdown supported
- Paragraph breaks allowed
- camelCase hashtags (#MachineLearning #AI)
- No trailing period in most cases

**Emoji Usage**:
- Similar to X (sparingly)
- More allowed due to length

**Hashtag Strategy**:
- Similar to X (camelCase, max 3 hashtags)
- Use relevant tags

**Markdown Usage**:
- Supported
- Plain text preferred
- Use sparingly

**Community Guidelines**:
- Follow Mastodon-specific community guidelines
- Be respectful of all users
- Avoid harassment
- Engage with community

---

## Examples and Best Practices

### LinkedIn Example

**Title**: Understanding Machine Learning in AI Alignment Research

**Summary**:
Machine learning is transforming AI alignment research, enabling more precise modeling of human values. This article explores how ML techniques are being used to improve AI alignment.

**Tags**: #AI #MachineLearning #Research #AIAlignment #MachineIntelligence

**Link**: See full article

**Best Practices**:
- Professional tone
- Paragraph breaks for readability
- Clear structure
- Relevant hashtags
- Professional emoji usage

### X Example

**Short Post**:
Machine learning is transforming AI alignment research, enabling more precise modeling of human values. 🤖 #AI #MachineLearning #Research

**Thread Starter**:
Why AI Alignment is Critical for the Future of AI

**Thread Continuation**:
1. AI alignment is about ensuring AI systems behave as intended
2. Recent advances in ML have made alignment more precise
3. However, new challenges are emerging

**Hashtag Example**:
#MachineLearning #AI #Research (camelCase, max 3 hashtags)

**Best Practices**:
- Strong hook in first line
- Short and punchy
- Conversational tone
- camelCase hashtags
- Clear thread structure

### Mastodon Example

**Same content format as before**:
Machine learning is transforming AI alignment research, enabling more precise modeling of human values.

**Markdown Example**:
**Title**: Understanding Machine Learning in AI Alignment Research

**Content**:
Machine learning is transforming AI alignment research, enabling more precise modeling of human values. This article explores how ML techniques are being used to improve AI alignment.

**Tags**: #AI #MachineLearning #Research #AIAlignment #MachineIntelligence

**Best Practices**:
- Markdown supported
- Paragraph breaks allowed
- Community-focused tone
- Relevant hashtags

---

## Content Adaptation Workflow

### Input Content

**Content Structure**:
- Title (optional, for LinkedIn)
- Summary (required for LinkedIn)
- Tags (optional, for LinkedIn and Mastodon)
- Content (required for all platforms)
- Link (optional, for all platforms)

### Automatic Adaptation

**LinkedIn**:
- Extract title (max 300 characters)
- Extract summary (max 3000 characters)
- Extract tags (max 5 tags, max 25 characters each)
- Remove markdown
- Format hashtags as #Hashtag (camelCase)

**X**:
- Strip markdown
- Truncate content to 280 characters (with ellipsis)
- Format hashtags as #Hashtag (camelCase)
- Max 3 hashtags
- No paragraph breaks

**Mastodon**:
- Keep existing behavior
- Format hashtags as #Hashtag (camelCase)
- Max 3 hashtags

### Manual Adaptation

**When to Use Manual Adaptation**:
- Content requires significant changes
- Complex formatting required
- Platform-specific content needs
- Manual review required

**Manual Adaptation Steps**:
1. Read original content
2. Adapt for target platform
3. Check character limits
4. Check formatting rules
5. Check hashtag rules
6. Review tone and cultural norms
7. Final review

### Review Process

**Before Publishing**:
1. Check character limits
2. Check field limits
3. Check formatting rules
4. Check tone guidelines
5. Check hashtag rules
6. Check cultural norms
7. Review for errors
8. Final check

---

## Do's and Don'ts

### LinkedIn

**Do's**:
- ✅ Use professional tone
- ✅ Provide insights and value
- ✅ Use paragraph breaks for readability
- ✅ Include relevant hashtags (max 5, max 25 characters each)
- ✅ Use bullet points for lists
- ✅ Include "See full article" link
- ✅ Respond to comments professionally
- ✅ Post 1-2 times per day

**Don'ts**:
- ❌ Use promotional language
- ❌ Use excessive emojis
- ❌ Use trailing period in title
- ❌ Exceed character limits
- ❌ Use incorrect hashtag format (lowercase)
- ❌ Ignore link requirements
- ❌ Post promotional content
- ❌ Use markdown excessively

### X (Twitter)

**Do's**:
- ✅ Use short, punchy tone
- ✅ Include strong hook in first line
- ✅ Use camelCase hashtags (#MachineLearning)
- ✅ Max 3 hashtags per tweet
- ✅ Use thread format for longer content
- ✅ Encourage replies
- ✅ Post 10 times per day (but spread out)

**Don'ts**:
- ❌ Use promotional language
- ❌ Use excessive emojis
- ❌ Use lowercase hashtags (#machinelearning)
- ❌ Use more than 3 hashtags
- ❌ Use paragraph breaks
- ❌ Post excessive promotional content
- ❌ Ignore thread structure

### Mastodon

**Do's**:
- ✅ Use community-focused tone
- ✅ Follow community guidelines
- ✅ Use camelCase hashtags (#MachineLearning)
- ✅ Max 3 hashtags per post
- ✅ Use markdown sparingly
- ✅ Engage with community
- ✅ Post at reasonable frequency (1 post per 2 minutes recommended)

**Don'ts**:
- ❌ Use promotional language
- ❌ Use excessive emojis
- ❌ Use lowercase hashtags
- ❌ Use more than 3 hashtags
- ❌ Ignore community guidelines
- ❌ Use excessive markdown
- ❌ Spam community

---

## Cross-Platform Uniqueness Requirements

**FR7.1**: No Identical Cross-Posting

The system MUST NOT post identical content across LinkedIn, X, and Mastodon. Each platform requires:
- Different hooks and tone
- Different hashtag strategies
- Different character limits applied
- Platform-specific field extraction (LinkedIn title/summary/tags)

**Minimum 10% difference required** between platform posts.

---

## AI Detection Compliance Guidelines

**FR6.1**: Avoid Overuse of Exclamation Marks
- Use exclamation marks sparingly (max 1 per post)
- Avoid multiple exclamation marks in sequence
- Natural excitement level only

**FR6.2**: Avoid Repetitive Sentence Structures
- Vary sentence lengths (mix short and long)
- Use different sentence starters
- Natural flow and rhythm

**FR6.3**: Use Natural Language Patterns
- Include contractions (I'm, don't, can't)
- Use idioms and colloquialisms appropriately
- Natural writing patterns

**FR6.4**: Avoid AI Vocabulary
- Replace 'ensure', 'leverage', 'robust', 'cutting-edge' with natural alternatives
- Use simpler, more direct language
- Focus on clarity over buzzwords

**FR6.5**: Vary Content Length
- LinkedIn: 200-3000 chars for professional depth
- X: 10-280 chars for punchy impact
- Mastodon: 500 chars for community discussion

**FR6.6**: Use Human-Like Formatting
- Natural paragraph breaks
- Appropriate emoji usage (sparingly)
- Real examples and anecdotes

## Anti-Detection Best Practices

- Randomized posting times (within reasonable hours)
- Vary content structure per platform
- Use real examples and data
- Engage with questions and discussion prompts
- Mix content types (opinion, news, research, personal)


---

## What's New

### Version 1.0 (2026-07-08)
- Comprehensive platform requirements documentation
- Character limits and field limits documented
- Authentication requirements and flows documented
- Rate limits and backoff strategies documented
- Content sharing advice and tone guidelines documented
- Cultural norms and formatting rules documented
- Examples and templates provided
- Content adaptation workflow documented
- AI detection compliance guidelines documented
- Anti-detection best practices documented
- Content quality guidelines documented
