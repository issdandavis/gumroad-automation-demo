package main

import (
	"crypto/md5"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"github.com/google/uuid"
)

// MessageType represents the type of universal message
type MessageType string

const (
	AIRequest       MessageType = "ai_request"
	AIResponse      MessageType = "ai_response"
	CodeTranslation MessageType = "code_translation"
	FunctionCall    MessageType = "function_call"
	DataSync        MessageType = "data_sync"
	HealthCheck     MessageType = "health_check"
	Error           MessageType = "error"
)

// CommunicationChannel represents the communication method
type CommunicationChannel string

const (
	WebSocket     CommunicationChannel = "websocket"
	HTTP          CommunicationChannel = "http"
	FileSystem    CommunicationChannel = "file_system"
	Database      CommunicationChannel = "database"
	BinarySocket  CommunicationChannel = "binary_socket"
	SharedMemory  CommunicationChannel = "shared_memory"
)

// UniversalMessage represents a message in the universal protocol
type UniversalMessage struct {
	ID              string                `json:"id"`
	Timestamp       string                `json:"timestamp"`
	MessageType     MessageType           `json:"message_type"`
	SourceLanguage  string                `json:"source_language"`
	TargetLanguage  string                `json:"target_language"`
	Payload         map[string]interface{} `json:"payload"`
	ResponseChannel CommunicationChannel  `json:"response_channel"`
	Checksum        string                `json:"checksum"`
}

// NewUniversalMessage creates a new universal message
func NewUniversalMessage(messageType MessageType, sourceLanguage, targetLanguage string, payload map[string]interface{}, responseChannel CommunicationChannel) *UniversalMessage {
	if targetLanguage == "" {
		targetLanguage = "universal"
	}
	if payload == nil {
		payload = make(map[string]interface{})
	}

	msg := &UniversalMessage{
		ID:              uuid.New().String(),
		Timestamp:       time.Now().UTC().Format(time.RFC3339),
		MessageType:     messageType,
		SourceLanguage:  sourceLanguage,
		TargetLanguage:  targetLanguage,
		Payload:         payload,
		ResponseChannel: responseChannel,
	}

	msg.Checksum = msg.calculateChecksum()
	return msg
}

// calculateChecksum calculates the message checksum for integrity
func (m *UniversalMessage) calculateChecksum() string {
	// Sort payload keys for consistent checksum
	payloadJSON, _ := json.Marshal(m.Payload)
	content := fmt.Sprintf("%s%s%s%s", m.ID, m.Timestamp, m.MessageType, string(payloadJSON))
	
	hash := md5.Sum([]byte(content))
	return fmt.Sprintf("%x", hash)
}

// ToJSON converts the message to JSON string
func (m *UniversalMessage) ToJSON() (string, error) {
	jsonBytes, err := json.MarshalIndent(m, "", "  ")
	if err != nil {
		return "", err
	}
	return string(jsonBytes), nil
}

// FromJSON creates a UniversalMessage from JSON string
func FromJSON(jsonStr string) (*UniversalMessage, error) {
	var msg UniversalMessage
	err := json.Unmarshal([]byte(jsonStr), &msg)
	if err != nil {
		return nil, err
	}

	// Verify checksum
	expectedChecksum := msg.calculateChecksum()
	if msg.Checksum != expectedChecksum {
		return nil, fmt.Errorf("message checksum mismatch - data may be corrupted")
	}

	return &msg, nil
}

// GoBridge represents the Go implementation of the Universal Bridge
type GoBridge struct {
	bridgeURL       string
	messageHandlers map[MessageType]func(*UniversalMessage) error
	isConnected     bool
}

// NewGoBridge creates a new Go bridge instance
func NewGoBridge(bridgeURL string) *GoBridge {
	if bridgeURL == "" {
		bridgeURL = "ws://localhost:8765"
	}

	bridge := &GoBridge{
		bridgeURL:       bridgeURL,
		messageHandlers: make(map[MessageType]func(*UniversalMessage) error),
		isConnected:     false,
	}

	bridge.connect()
	return bridge
}

// connect establishes connection to the Universal Bridge
func (gb *GoBridge) connect() error {
	fmt.Println("🔌 Connecting to Universal Bridge...")

	// Ensure directories exist
	err := gb.ensureDirectories()
	if err != nil {
		return fmt.Errorf("failed to create directories: %v", err)
	}

	// Start file watcher
	go gb.startFileWatcher()

	gb.isConnected = true
	fmt.Println("✅ Connected to Universal Bridge")
	return nil
}

// ensureDirectories creates necessary directories
func (gb *GoBridge) ensureDirectories() error {
	dirs := []string{
		"bridge_messages/go",
		"bridge_messages/incoming",
		"bridge_messages/outgoing",
	}

	for _, dir := range dirs {
		err := os.MkdirAll(dir, 0755)
		if err != nil {
			return err
		}
	}

	return nil
}

// startFileWatcher watches for incoming messages
func (gb *GoBridge) startFileWatcher() {
	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		gb.processIncomingMessages()
	}
}

// processIncomingMessages processes messages from the file system
func (gb *GoBridge) processIncomingMessages() {
	incomingDir := "bridge_messages/go"
	
	files, err := ioutil.ReadDir(incomingDir)
	if err != nil {
		return // Directory might not exist yet
	}

	for _, file := range files {
		if strings.HasSuffix(file.Name(), ".json") {
			filePath := filepath.Join(incomingDir, file.Name())
			
			content, err := ioutil.ReadFile(filePath)
			if err != nil {
				log.Printf("❌ Error reading file %s: %v", filePath, err)
				continue
			}

			message, err := FromJSON(string(content))
			if err != nil {
				log.Printf("❌ Error parsing message %s: %v", filePath, err)
				continue
			}

			err = gb.handleIncomingMessage(message)
			if err != nil {
				log.Printf("❌ Error handling message %s: %v", message.ID, err)
				continue
			}

			// Move to processed
			processedDir := filepath.Join(incomingDir, "processed")
			os.MkdirAll(processedDir, 0755)
			os.Rename(filePath, filepath.Join(processedDir, file.Name()))
		}
	}
}

// handleIncomingMessage handles an incoming message
func (gb *GoBridge) handleIncomingMessage(message *UniversalMessage) error {
	fmt.Printf("📥 Received message: %s (%s)\n", message.ID, message.MessageType)

	handler, exists := gb.messageHandlers[message.MessageType]
	if exists {
		return handler(message)
	}

	fmt.Printf("⚠️ No handler for message type: %s\n", message.MessageType)
	return nil
}

// SendMessage sends a message through the universal bridge
func (gb *GoBridge) SendMessage(message *UniversalMessage) (string, error) {
	if !gb.isConnected {
		return "", fmt.Errorf("not connected to Universal Bridge")
	}

	// Send via file system
	jsonStr, err := message.ToJSON()
	if err != nil {
		return "", err
	}

	outgoingPath := filepath.Join("bridge_messages/incoming", message.ID+".json")
	err = ioutil.WriteFile(outgoingPath, []byte(jsonStr), 0644)
	if err != nil {
		return "", err
	}

	fmt.Printf("📤 Message sent: %s (%s → %s)\n", message.ID, message.SourceLanguage, message.TargetLanguage)
	return message.ID, nil
}

// OnMessage registers a handler for a specific message type
func (gb *GoBridge) OnMessage(messageType MessageType, handler func(*UniversalMessage) error) {
	gb.messageHandlers[messageType] = handler
	fmt.Printf("📝 Registered handler for %s\n", messageType)
}

// RequestAI sends an AI request
func (gb *GoBridge) RequestAI(prompt, instructions string, context map[string]interface{}) (string, error) {
	if context == nil {
		context = make(map[string]interface{})
	}

	payload := map[string]interface{}{
		"action":       "generate_content",
		"prompt":       prompt,
		"instructions": instructions,
		"context":      context,
	}

	message := NewUniversalMessage(AIRequest, "go", "universal", payload, FileSystem)
	return gb.SendMessage(message)
}

// TranslateCode translates code to another language
func (gb *GoBridge) TranslateCode(code, targetLanguage string) (string, error) {
	payload := map[string]interface{}{
		"code": code,
	}

	message := NewUniversalMessage(CodeTranslation, "go", targetLanguage, payload, FileSystem)
	return gb.SendMessage(message)
}

// CallFunction calls a function in another language
func (gb *GoBridge) CallFunction(targetLanguage, functionName string, args []interface{}, kwargs map[string]interface{}) (string, error) {
	if args == nil {
		args = make([]interface{}, 0)
	}
	if kwargs == nil {
		kwargs = make(map[string]interface{})
	}

	payload := map[string]interface{}{
		"function_name": functionName,
		"args":          args,
		"kwargs":        kwargs,
	}

	message := NewUniversalMessage(FunctionCall, "go", targetLanguage, payload, FileSystem)
	return gb.SendMessage(message)
}

// Go-specific AI helpers

// GenerateGoStruct generates a Go struct based on description
func (gb *GoBridge) GenerateGoStruct(description string, fields []string) (string, error) {
	fieldsStr := strings.Join(fields, ", ")
	context := map[string]interface{}{
		"language": "go",
		"type":     "struct_generation",
	}

	return gb.RequestAI(
		fmt.Sprintf("Generate a Go struct: %s", description),
		fmt.Sprintf("Fields: %s. Use proper Go naming conventions and include JSON tags.", fieldsStr),
		context,
	)
}

// OptimizeGoCode optimizes Go code
func (gb *GoBridge) OptimizeGoCode(code string) (string, error) {
	context := map[string]interface{}{
		"language": "go",
		"type":     "code_optimization",
	}

	return gb.RequestAI(
		fmt.Sprintf("Optimize this Go code: %s", code),
		"Focus on performance, memory usage, and Go best practices. Return only the optimized code.",
		context,
	)
}

// GenerateGoTests generates Go tests
func (gb *GoBridge) GenerateGoTests(code string) (string, error) {
	context := map[string]interface{}{
		"language": "go",
		"type":     "test_generation",
	}

	return gb.RequestAI(
		fmt.Sprintf("Generate Go tests for this code: %s", code),
		"Create comprehensive unit tests with table-driven tests. Use testing package.",
		context,
	)
}

// Demo function
func demoGoBridge() {
	fmt.Println("🌍 GO UNIVERSAL BRIDGE DEMO")
	fmt.Println(strings.Repeat("=", 50))

	bridge := NewGoBridge("")

	// Wait for connection
	time.Sleep(1 * time.Second)

	// Set up message handlers
	bridge.OnMessage(AIResponse, func(message *UniversalMessage) error {
		fmt.Printf("🤖 AI Response received: %+v\n", message.Payload)
		return nil
	})

	bridge.OnMessage(CodeTranslation, func(message *UniversalMessage) error {
		fmt.Printf("🔄 Code translation received: %+v\n", message.Payload)
		return nil
	})

	// Demo 1: AI request
	fmt.Println("\n🤖 Demo 1: AI Request from Go")
	context := map[string]interface{}{
		"project":  "App Productizer",
		"priority": "high",
	}
	bridge.RequestAI(
		"Create a Go function that validates email addresses",
		"Use standard library and include error handling",
		context,
	)

	// Demo 2: Code translation
	fmt.Println("\n🔄 Demo 2: Translate Go to Python")
	goCode := `
func calculateTotal(items []Item) float64 {
	var total float64
	for _, item := range items {
		total += item.Price
	}
	return total
}
`
	bridge.TranslateCode(goCode, "python")

	// Demo 3: Function call to Python
	fmt.Println("\n📞 Demo 3: Call Python function from Go")
	args := []interface{}{goCode}
	kwargs := map[string]interface{}{
		"format":           "markdown",
		"include_examples": true,
	}
	bridge.CallFunction("python", "generate_documentation", args, kwargs)

	// Demo 4: Go-specific AI helpers
	fmt.Println("\n⚡ Demo 4: Go-specific AI helpers")
	bridge.GenerateGoStruct(
		"A struct representing a user profile",
		[]string{"ID", "Name", "Email", "CreatedAt"},
	)

	bridge.OptimizeGoCode(`
func slowFunction(arr []int) []int {
	var result []int
	for i := 0; i < len(arr); i++ {
		for j := 0; j < len(arr); j++ {
			if arr[i] == arr[j] && i != j {
				result = append(result, arr[i])
			}
		}
	}
	return result
}
`)

	fmt.Println("\n✅ Go Bridge Demo Complete")
	fmt.Println("📁 Check bridge_messages/ directory for message files")
}

func main() {
	demoGoBridge()
}